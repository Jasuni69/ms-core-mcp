import asyncio
import io
from typing import Any, Dict, Optional, Tuple

from mcp.server.fastmcp import Context

from helpers.clients.fabric_client import FabricApiClient
from helpers.clients.onelake_client import OneLakeClient
from helpers.clients.sql_client import SQLClient, get_sql_endpoint
from helpers.utils.authentication import get_azure_credentials
from helpers.utils.context import mcp, __ctx_cache
from helpers.logging_config import get_logger


logger = get_logger(__name__)


async def _resolve_sql_client(
    ctx: Context,
    workspace: Optional[str],
    lakehouse: Optional[str],
    warehouse: Optional[str],
    resource_type: Optional[str],
) -> Tuple[SQLClient, Dict[str, Any], str, str, Any]:
    if ctx is None:
        raise ValueError("Context (ctx) must be provided.")

    ws = workspace or __ctx_cache.get(f"{ctx.client_id}_workspace")
    if not ws:
        raise ValueError("Workspace must be specified or set with set_workspace.")

    resolved_type = (resource_type or "").lower()
    if not resolved_type:
        lakehouse = lakehouse or __ctx_cache.get(f"{ctx.client_id}_lakehouse")
        warehouse = warehouse or __ctx_cache.get(f"{ctx.client_id}_warehouse")
        if lakehouse:
            resolved_type = "lakehouse"
        elif warehouse:
            resolved_type = "warehouse"

    if resolved_type == "lakehouse" and not (lakehouse or __ctx_cache.get(f"{ctx.client_id}_lakehouse")):
        raise ValueError(
            "Lakehouse must be specified either in the call or via set_lakehouse."
        )
    if resolved_type == "warehouse" and not (warehouse or __ctx_cache.get(f"{ctx.client_id}_warehouse")):
        raise ValueError(
            "Warehouse must be specified either in the call or via set_warehouse."
        )
    if resolved_type not in {"lakehouse", "warehouse"}:
        raise ValueError("Type must be 'lakehouse' or 'warehouse'.")

    credential = get_azure_credentials(ctx.client_id, __ctx_cache)
    name, endpoint = await get_sql_endpoint(
        workspace=ws,
        lakehouse=lakehouse or __ctx_cache.get(f"{ctx.client_id}_lakehouse"),
        warehouse=warehouse or __ctx_cache.get(f"{ctx.client_id}_warehouse"),
        type=resolved_type,
        credential=credential,
    )

    if not endpoint:
        raise ValueError(
            f"Failed to resolve SQL endpoint for {resolved_type} '{lakehouse or warehouse}'."
        )

    sql_client = SQLClient(endpoint["server"], endpoint["database"], credential)
    return sql_client, endpoint, resolved_type, ws, credential


async def _resolve_lakehouse_ids(
    credential,
    workspace_id: str,
    lakehouse: str,
) -> Tuple[str, str]:
    fabric_client = FabricApiClient(credential)
    name, lakehouse_id = await fabric_client.resolve_item_name_and_id(
        item=lakehouse,
        type="Lakehouse",
        workspace=workspace_id,
    )
    return name, str(lakehouse_id)


def _prepare_rows(df, max_rows: int) -> Tuple[int, int, Any]:
    total_rows = df.height
    limited_df = df if max_rows <= 0 else df.head(max_rows)
    return total_rows, limited_df.height, limited_df.to_dicts()


@mcp.tool()
async def sql_query(
    query: str,
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    warehouse: Optional[str] = None,
    type: Optional[str] = None,
    max_rows: int = 100,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Run a SQL query against a lakehouse or warehouse endpoint."""

    try:
        client, endpoint, resolved_type, workspace_id, credential = await _resolve_sql_client(
            ctx, workspace, lakehouse, warehouse, type
        )
        df = await asyncio.to_thread(client.run_query, query)

        if df.is_empty():
            return {
                "message": "Query executed successfully but returned no rows.",
                "resource": endpoint,
            }

        total_rows, returned_rows, rows = _prepare_rows(df, max_rows)

        return {
            "resource": endpoint,
            "rowCount": total_rows,
            "returnedRows": returned_rows,
            "rows": rows,
            "truncated": total_rows > returned_rows,
        }
    except Exception as exc:
        logger.error("SQL query failed: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def sql_explain(
    query: str,
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    warehouse: Optional[str] = None,
    type: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Retrieve an estimated execution plan for a query."""

    explain_query = f"EXPLAIN {query}"
    try:
        result = await sql_query(
            query=explain_query,
            workspace=workspace,
            lakehouse=lakehouse,
            warehouse=warehouse,
            type=type,
            max_rows=200,
            ctx=ctx,
        )
        if "error" in result:
            raise ValueError(result["error"])
        result["originalQuery"] = query
        return result
    except Exception as exc:
        logger.warning("EXPLAIN failed with message '%s'. Falling back to SHOWPLAN.", exc)
        try:
            showplan_query = (
                "SET SHOWPLAN_XML ON; "
                + query
                + "; SET SHOWPLAN_XML OFF;"
            )
            return await sql_query(
                query=showplan_query,
                workspace=workspace,
                lakehouse=lakehouse,
                warehouse=warehouse,
                type=type,
                max_rows=1,
                ctx=ctx,
            )
        except Exception as inner_exc:
            logger.error("Showplan retrieval failed: %s", inner_exc)
            return {"error": str(inner_exc)}


@mcp.tool()
async def sql_export(
    query: str,
    target_path: str,
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    warehouse: Optional[str] = None,
    type: Optional[str] = None,
    export_lakehouse: Optional[str] = None,
    file_format: str = "csv",
    overwrite: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Export query results to OneLake as CSV or Parquet."""

    try:
        client, endpoint, resolved_type, workspace_id, credential = await _resolve_sql_client(
            ctx, workspace, lakehouse, warehouse, type
        )
        df = await asyncio.to_thread(client.run_query, query)

        if df.is_empty():
            return {"message": "Query produced no rows; nothing exported."}

        buffer = io.BytesIO()
        fmt = file_format.lower()
        if fmt == "csv":
            df.write_csv(buffer)
            encoding = "utf-8"
        elif fmt == "parquet":
            df.write_parquet(buffer)
            encoding = "binary"
        else:
            raise ValueError("file_format must be either 'csv' or 'parquet'.")

        if resolved_type == "lakehouse":
            export_resource = endpoint["resourceId"]
        else:
            export_resource = export_lakehouse or lakehouse or __ctx_cache.get(
                f"{ctx.client_id}_lakehouse"
            )
            if not export_resource:
                raise ValueError(
                    "Specify export_lakehouse when exporting from a warehouse."
                )

        _, export_lakehouse_id = await _resolve_lakehouse_ids(
            credential, endpoint["workspaceId"], export_resource
        )

        onelake_client = OneLakeClient(credential)
        await onelake_client.write_file(
            endpoint["workspaceId"], export_lakehouse_id, target_path, buffer.getvalue(), overwrite
        )

        return {
            "rowsExported": df.height,
            "format": fmt,
            "targetPath": target_path,
            "lakehouseId": export_lakehouse_id,
            "workspaceId": endpoint["workspaceId"],
            "encoding": encoding,
        }
    except Exception as exc:
        logger.error("SQL export failed: %s", exc)
        return {"error": str(exc)}


