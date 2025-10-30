import struct
import urllib.parse
from itertools import chain, repeat
from typing import Any, Dict, Optional, Tuple

import polars as pl
from azure.identity import DefaultAzureCredential
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import ResourceClosedError

from helpers.logging_config import get_logger
from helpers.clients.fabric_client import FabricApiClient
from helpers.clients.lakehouse_client import LakehouseClient
from helpers.clients.warehouse_client import WarehouseClient


logger = get_logger(__name__)

DRIVER = "{ODBC Driver 18 for SQL Server}"
RESOURCE_URL = "https://database.windows.net/.default"


def _build_access_token_bytes(token: str) -> bytes:
    token_as_bytes = token.encode("utf-8")
    encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
    return struct.pack("<i", len(encoded_bytes)) + encoded_bytes


def _parse_connection_string(connection_string: str) -> Tuple[str, str]:
    if not connection_string:
        raise ValueError("Connection string is empty.")

    components: Dict[str, str] = {}
    for segment in connection_string.split(";"):
        if not segment or "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        components[key.strip().lower()] = value.strip()

    server = components.get("data source") or components.get("server")
    database = components.get("initial catalog") or components.get("database")

    if not server or not database:
        raise ValueError("Unable to parse server or database from connection string.")

    return server, database


def _create_engine(
    server: str,
    database: str,
    credential: DefaultAzureCredential,
    driver: str = DRIVER,
) -> Engine:
    connection_string = (
        f"Driver={driver};Server={server};Database={database};Encrypt=Yes;TrustServerCertificate=No"
    )
    params = urllib.parse.quote(connection_string)

    token = credential.get_token(RESOURCE_URL)
    attrs_before = {1256: _build_access_token_bytes(token.token)}

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        connect_args={"attrs_before": attrs_before},
    )


async def get_sql_endpoint(
    workspace: Optional[str] = None,
    lakehouse: Optional[str] = None,
    warehouse: Optional[str] = None,
    type: Optional[str] = None,
    credential: Optional[DefaultAzureCredential] = None,
) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
    try:
        credential = credential or DefaultAzureCredential()
        client = FabricApiClient(credential)

        _, workspace_id = await client.resolve_workspace_name_and_id(workspace)

        connection_string: Optional[str] = None
        resource_name: Optional[str] = None
        resource_id: Optional[str] = None

        if type and type.lower() == "lakehouse":
            lakehouse_client = LakehouseClient(client)
            resource_name, resource_id = await client.resolve_item_name_and_id(
                workspace=workspace_id, item=lakehouse, type="Lakehouse"
            )
            lakehouse_obj = await lakehouse_client.get_lakehouse(
                workspace=workspace, lakehouse=resource_id
            )
            connection_string = (
                lakehouse_obj.get("properties", {})
                .get("sqlEndpointProperties", {})
                .get("connectionString")
            )
        elif type and type.lower() == "warehouse":
            warehouse_client = WarehouseClient(client)
            resource_name, resource_id = await client.resolve_item_name_and_id(
                workspace=workspace_id, item=warehouse, type="Warehouse"
            )
            warehouse_obj = await warehouse_client.get_warehouse(
                workspace=workspace, warehouse=resource_id
            )
            connection_string = (
                warehouse_obj.get("properties", {})
                .get("connectionString")
            )
        else:
            raise ValueError("Type must be 'lakehouse' or 'warehouse'.")

        if not connection_string:
            return None, None

        server, database = _parse_connection_string(connection_string)
        return resource_name, {
            "workspaceId": workspace_id,
            "resourceId": resource_id,
            "server": server,
            "database": database,
            "connectionString": connection_string,
        }
    except Exception as exc:
        logger.error("Failed to resolve SQL endpoint: %s", exc)
        return None, None


class SQLClient:
    def __init__(
        self,
        server: str,
        database: str,
        credential: DefaultAzureCredential,
    ) -> None:
        self.engine = _create_engine(server, database, credential)

    def run_query(self, query: str) -> pl.DataFrame:
        return pl.read_database(query, connection=self.engine)

    def load_data(
        self,
        df: pl.DataFrame,
        table_name: str,
        if_exists: str = "append",
    ) -> None:
        pdf = df.to_pandas()
        pdf.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False)

    def execute(self, statement: str) -> Dict[str, Any]:
        """Execute a SQL statement that may not return a result set."""

        with self.engine.connect() as connection:
            result = connection.exec_driver_sql(statement)
            response: Dict[str, Any] = {"rowcount": result.rowcount}
            try:
                rows = result.fetchall()
                columns = list(result.keys())
                response["columns"] = columns
                response["rows"] = [dict(zip(columns, row)) for row in rows]
            except ResourceClosedError:
                response["columns"] = []
                response["rows"] = []
            return response
