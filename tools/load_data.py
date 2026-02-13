from helpers.utils.context import mcp, __ctx_cache
from mcp.server.fastmcp import Context
from helpers.utils.authentication import get_azure_credentials
from helpers.clients import (
    FabricApiClient,
    LakehouseClient,
    WarehouseClient,
    get_sql_endpoint,
)
from helpers.logging_config import get_logger
import tempfile
import os
import requests
from typing import Optional

logger = get_logger(__name__)


@mcp.tool()
async def load_data_from_url(
    url: str,
    destination_table: str,
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    warehouse: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Load data from a URL into a table in a warehouse or lakehouse.

    Args:
        url: The URL to download data from (CSV or Parquet supported).
        destination_table: The name of the table to load data into.
        workspace: Name or ID of the workspace (optional).
        lakehouse: Name or ID of the lakehouse (optional).
        warehouse: Name or ID of the warehouse (optional).
        ctx: Context object containing client information.
    Returns:
        A string confirming the data load or an error message.
    """
    try:
        # Download the file
        response = requests.get(url)
        if response.status_code != 200:
            return f"Failed to download file from URL: {url}"
        file_ext = url.split("?")[0].split(".")[-1].lower()
        if file_ext not in ("csv", "parquet"):
            return f"Unsupported file type: {file_ext}. Only CSV and Parquet are supported."
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file_ext}"
        ) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        # Choose destination: lakehouse or warehouse
        credential = get_azure_credentials(ctx.client_id, __ctx_cache)
        fabric_client = FabricApiClient(credential)

        workspace_ref = workspace or __ctx_cache.get(f"{ctx.client_id}_workspace")
        if not workspace_ref:
            os.remove(tmp_path)
            return "Workspace not set. Please set a workspace using set_workspace."

        resource_type = None
        resource_ref = None
        if lakehouse:
            resource_type = "lakehouse"
            resource_ref = lakehouse
        elif warehouse:
            resource_type = "warehouse"
            resource_ref = warehouse
        else:
            os.remove(tmp_path)
            return "Either lakehouse or warehouse must be specified."

        try:
            # Read data with polars
            import polars as pl

            if file_ext == "csv":
                df = pl.read_csv(tmp_path)
            else:
                df = pl.read_parquet(tmp_path)

            row_count = len(df)

            # Get SQL endpoint for loading
            _, endpoint = await get_sql_endpoint(
                workspace=workspace_ref,
                **{resource_type: resource_ref},
                type=resource_type,
                credential=credential,
            )
            if not endpoint:
                os.remove(tmp_path)
                return f"Unable to resolve SQL endpoint for {resource_type} '{resource_ref}'."

            from helpers.clients.sql_client import SQLClient
            sql_client = SQLClient(endpoint["server"], endpoint["database"], credential)

            import asyncio
            await asyncio.to_thread(
                sql_client.load_data, df, destination_table, "replace"
            )

            return f"Loaded {row_count} rows from {url} into table '{destination_table}' in {resource_type} '{resource_ref}'."
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        return f"Error loading data: {str(e)}"


# @mcp.resource(
#         uri="tables://{table_name}",
# )
