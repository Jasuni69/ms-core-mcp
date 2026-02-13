import asyncio
from typing import Any, Dict, List, Optional

from helpers.utils.context import mcp, __ctx_cache
from mcp.server.fastmcp import Context
from helpers.utils.authentication import get_azure_credentials
from helpers.clients import (
    FabricApiClient,
    TableClient,
    SQLClient,
    get_sql_endpoint,
)
from helpers.logging_config import get_logger


logger = get_logger(__name__)


async def _resolve_workspace_lakehouse(
    ctx: Context,
    workspace: Optional[str],
    lakehouse: Optional[str],
) -> Dict[str, Any]:
    if ctx is None:
        raise ValueError("Context (ctx) must be provided.")

    credential = get_azure_credentials(ctx.client_id, __ctx_cache)
    fabric_client = FabricApiClient(credential)

    workspace_ref = workspace or __ctx_cache.get(f"{ctx.client_id}_workspace")
    if not workspace_ref:
        raise ValueError("Workspace must be specified or set via set_workspace.")

    workspace_name, workspace_id = await fabric_client.resolve_workspace_name_and_id(
        workspace_ref
    )

    lakehouse_ref = lakehouse or __ctx_cache.get(f"{ctx.client_id}_lakehouse")
    if not lakehouse_ref:
        raise ValueError("Lakehouse must be specified or set via set_lakehouse.")

    lakehouse_name, lakehouse_id = await fabric_client.resolve_item_name_and_id(
        item=lakehouse_ref,
        type="Lakehouse",
        workspace=workspace_id,
    )

    return {
        "credential": credential,
        "fabric_client": fabric_client,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "workspace_ref": workspace_ref,
        "lakehouse_id": str(lakehouse_id),
        "lakehouse_name": lakehouse_name,
        "lakehouse_ref": lakehouse_ref,
    }


async def _resolve_lakehouse_and_table(
    ctx: Context,
    workspace: Optional[str],
    lakehouse: Optional[str],
    table_name: Optional[str],
) -> Dict[str, Any]:
    context = await _resolve_workspace_lakehouse(ctx, workspace, lakehouse)

    table_ref = table_name or __ctx_cache.get(f"{ctx.client_id}_table")
    if not table_ref:
        raise ValueError(
            "Table must be specified or set via set_table before using this command."
        )

    table_client = TableClient(context["fabric_client"])
    tables = await table_client.list_tables(
        context["workspace_id"], context["lakehouse_id"], "lakehouse"
    )
    if isinstance(tables, str):
        raise ValueError(tables)

    target = next(
        (
            t
            for t in tables
            if str(t.get("name", "")).lower() == str(table_ref).lower()
        ),
        None,
    )

    if not target:
        raise ValueError(
            f"Table '{table_ref}' not found in lakehouse '{context['lakehouse_name']}'."
        )

    schema_name = (
        target.get("schema")
        or target.get("schemaName")
        or target.get("schema_name")
        or "dbo"
    )
    identifier = f"[{schema_name}].[{target.get('name')}]"

    context.update(
        {
            "table": target,
            "table_name": target.get("name"),
            "schema": schema_name,
            "identifier": identifier,
            "table_client": table_client,
        }
    )
    return context


@mcp.tool()
async def set_table(table_name: str, ctx: Context) -> str:
    __ctx_cache[f"{ctx.client_id}_table"] = table_name
    return f"Table set to '{table_name}'."


@mcp.tool()
async def list_tables(
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    ctx: Context = None,
) -> Any:
    try:
        context = await _resolve_workspace_lakehouse(ctx, workspace, lakehouse)
        table_client = TableClient(context["fabric_client"])
        return await table_client.list_tables(
            context["workspace_id"], context["lakehouse_id"], "lakehouse"
        )
    except Exception as exc:
        logger.error("Error listing tables: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def get_lakehouse_table_schema(
    workspace: Optional[str],
    lakehouse: Optional[str],
    table_name: str = None,
    ctx: Context = None,
) -> Any:
    try:
        context = await _resolve_lakehouse_and_table(ctx, workspace, lakehouse, table_name)
        return await context["table_client"].get_table_schema(
            context["workspace_id"],
            context["lakehouse_id"],
            "lakehouse",
            context["table_name"],
            context["credential"],
        )
    except Exception as exc:
        logger.error("Error retrieving table schema: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def get_all_lakehouse_schemas(
    lakehouse: Optional[str],
    workspace: Optional[str] = None,
    ctx: Context = None,
) -> Any:
    try:
        context = await _resolve_workspace_lakehouse(ctx, workspace, lakehouse)
        table_client = TableClient(context["fabric_client"])
        return await table_client.get_all_schemas(
            context["workspace_id"],
            context["lakehouse_id"],
            "lakehouse",
            context["credential"],
        )
    except Exception as exc:
        logger.error("Error retrieving table schemas: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def table_preview(
    table: Optional[str] = None,
    lakehouse: Optional[str] = None,
    workspace: Optional[str] = None,
    limit: int = 50,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        context = await _resolve_lakehouse_and_table(ctx, workspace, lakehouse, table)

        _, endpoint = await get_sql_endpoint(
            workspace=context["workspace_ref"],
            lakehouse=context["lakehouse_name"],
            type="lakehouse",
            credential=context["credential"],
        )
        if not endpoint:
            raise ValueError("Unable to resolve SQL endpoint for the specified lakehouse.")

        client = SQLClient(
            endpoint["server"], endpoint["database"], context["credential"]
        )
        limit_clause = f"TOP {max(limit, 1)} " if limit and limit > 0 else ""
        query = f"SELECT {limit_clause}* FROM {context['identifier']}"
        df = await asyncio.to_thread(client.run_query, query)

        columns = list(df.columns)
        rows = [dict(zip(columns, row)) for row in df.rows()]

        return {
            "table": context["table_name"],
            "schema": context["schema"],
            "columns": columns,
            "rows": rows,
            "returnedRows": len(rows),
            "truncated": bool(limit and len(rows) >= max(limit, 1)),
        }
    except Exception as exc:
        logger.error("Error generating table preview: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def table_schema(
    table: Optional[str] = None,
    lakehouse: Optional[str] = None,
    workspace: Optional[str] = None,
    ctx: Context = None,
) -> Any:
    return await get_lakehouse_table_schema(workspace, lakehouse, table, ctx)


@mcp.tool()
async def describe_history(
    table: Optional[str] = None,
    lakehouse: Optional[str] = None,
    workspace: Optional[str] = None,
    limit: int = 20,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        context = await _resolve_lakehouse_and_table(ctx, workspace, lakehouse, table)

        _, endpoint = await get_sql_endpoint(
            workspace=context["workspace_ref"],
            lakehouse=context["lakehouse_name"],
            type="lakehouse",
            credential=context["credential"],
        )
        if not endpoint:
            raise ValueError("Unable to resolve SQL endpoint for the specified lakehouse.")

        client = SQLClient(
            endpoint["server"], endpoint["database"], context["credential"]
        )
        limit_clause = f" LIMIT {max(limit, 1)}" if limit and limit > 0 else ""
        query = f"DESCRIBE HISTORY {context['identifier']}{limit_clause}"
        df = await asyncio.to_thread(client.run_query, query)
        columns = list(df.columns)
        rows = [dict(zip(columns, row)) for row in df.rows()]

        return {
            "table": context["table_name"],
            "history": rows,
            "columns": columns,
            "returnedRows": len(rows),
        }
    except Exception as exc:
        logger.error("Error describing table history: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def optimize_delta(
    table: Optional[str] = None,
    lakehouse: Optional[str] = None,
    workspace: Optional[str] = None,
    zorder_by: Optional[List[str]] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        context = await _resolve_lakehouse_and_table(ctx, workspace, lakehouse, table)

        _, endpoint = await get_sql_endpoint(
            workspace=context["workspace_ref"],
            lakehouse=context["lakehouse_name"],
            type="lakehouse",
            credential=context["credential"],
        )
        if not endpoint:
            raise ValueError("Unable to resolve SQL endpoint for the specified lakehouse.")

        client = SQLClient(
            endpoint["server"], endpoint["database"], context["credential"]
        )
        if zorder_by:
            columns = ", ".join(f"[{col.strip()}]" for col in zorder_by if col)
            statement = f"OPTIMIZE {context['identifier']} ZORDER BY ({columns})"
        else:
            statement = f"OPTIMIZE {context['identifier']}"

        result = await asyncio.to_thread(client.execute, statement)
        result.update({"statement": statement})
        return result
    except Exception as exc:
        logger.error("Error optimizing delta table: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def vacuum_delta(
    table: Optional[str] = None,
    lakehouse: Optional[str] = None,
    workspace: Optional[str] = None,
    retain_hours: int = 168,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        context = await _resolve_lakehouse_and_table(ctx, workspace, lakehouse, table)

        _, endpoint = await get_sql_endpoint(
            workspace=context["workspace_ref"],
            lakehouse=context["lakehouse_name"],
            type="lakehouse",
            credential=context["credential"],
        )
        if not endpoint:
            raise ValueError("Unable to resolve SQL endpoint for the specified lakehouse.")

        client = SQLClient(
            endpoint["server"], endpoint["database"], context["credential"]
        )
        statement = (
            f"VACUUM {context['identifier']} RETAIN {max(retain_hours, 0)} HOURS"
        )
        result = await asyncio.to_thread(client.execute, statement)
        result.update({"statement": statement})
        return result
    except Exception as exc:
        logger.error("Error vacuuming delta table: %s", exc)
        return {"error": str(exc)}

