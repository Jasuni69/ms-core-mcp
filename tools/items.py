from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context

from helpers.clients import FabricApiClient
from helpers.logging_config import get_logger
from helpers.utils.authentication import get_azure_credentials
from helpers.utils.context import mcp, __ctx_cache


logger = get_logger(__name__)


def _resolve_workspace(ctx: Context, workspace: Optional[str]) -> str:
    ws = workspace or __ctx_cache.get(f"{ctx.client_id}_workspace")
    if not ws:
        raise ValueError(
            "Workspace not set. Provide a workspace parameter or call set_workspace first."
        )
    return ws


@mcp.tool()
async def resolve_item(
    workspace: Optional[str],
    name_or_id: str,
    type: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Resolve an item name or ID to its canonical ID and metadata."""

    try:
        if ctx is None:
            raise ValueError("Context is required for resolving items.")

        ws = _resolve_workspace(ctx, workspace)
        credential = get_azure_credentials(ctx.client_id, __ctx_cache)
        fabric_client = FabricApiClient(credential=credential)

        _, ws_id = await fabric_client.resolve_workspace_name_and_id(ws)

        item_name, item_id = await fabric_client.resolve_item_name_and_id(
            item=name_or_id,
            type=type,
            workspace=ws_id,
        )

        return {
            "displayName": item_name,
            "id": str(item_id),
            "type": type,
            "workspace": ws,
        }
    except Exception as exc:
        logger.error("Failed to resolve item '%s': %s", name_or_id, exc)
        return {"error": str(exc)}


@mcp.tool()
async def list_items(
    workspace: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    top: int = 100,
    skip: int = 0,
    ctx: Context = None,
) -> str:
    """List workspace items, optionally filtered by type or search term."""

    try:
        if ctx is None:
            raise ValueError("Context is required for listing items.")

        ws = _resolve_workspace(ctx, workspace)
        credential = get_azure_credentials(ctx.client_id, __ctx_cache)
        fabric_client = FabricApiClient(credential=credential)

        _, ws_id = await fabric_client.resolve_workspace_name_and_id(ws)

        params: Dict[str, Any] = {}
        if search:
            params["search"] = search
        if top:
            params["$top"] = min(max(top, 1), 500)
        if skip:
            params["$skip"] = max(skip, 0)

        items = await fabric_client.get_items(ws_id, item_type=type, params=params)

        if not items:
            return "No items found for the specified criteria."

        header = "| Name | ID | Type | State |\n"
        divider = "|---|---|---|---|\n"
        rows = []
        for item in items:
            rows.append(
                "| {name} | {id} | {type} | {state} |".format(
                    name=item.get("displayName", "N/A"),
                    id=item.get("id", "N/A"),
                    type=item.get("type", "N/A"),
                    state=item.get("state", "N/A"),
                )
            )

        return "# Workspace Items\n\n" + header + divider + "\n".join(rows)
    except Exception as exc:
        logger.error("Error listing items: %s", exc)
        return f"Error listing items: {exc}"


@mcp.tool()
async def get_permissions(
    workspace: Optional[str],
    item_id: str,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Retrieve the permission assignments for a workspace item."""

    try:
        if ctx is None:
            raise ValueError("Context is required for retrieving permissions.")

        ws = _resolve_workspace(ctx, workspace)
        credential = get_azure_credentials(ctx.client_id, __ctx_cache)
        fabric_client = FabricApiClient(credential=credential)

        _, ws_id = await fabric_client.resolve_workspace_name_and_id(ws)

        response = await fabric_client.get_item_permissions(ws_id, item_id)

        value: List[Dict[str, Any]]
        if isinstance(response, dict):
            value = response.get("value", [])
        elif isinstance(response, list):
            value = response
        else:
            value = []

        return {"itemId": item_id, "workspace": ws, "assignments": value}
    except Exception as exc:
        logger.error("Failed to get permissions for %s: %s", item_id, exc)
        return {"error": str(exc)}


@mcp.tool()
async def set_permissions(
    workspace: Optional[str],
    item_id: str,
    assignments: Optional[List[Dict[str, Any]]] = None,
    scope: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Set or update permissions for a workspace item."""

    try:
        if ctx is None:
            raise ValueError("Context is required for setting permissions.")
        if not assignments:
            raise ValueError("Assignments must be provided to set permissions.")

        ws = _resolve_workspace(ctx, workspace)
        credential = get_azure_credentials(ctx.client_id, __ctx_cache)
        fabric_client = FabricApiClient(credential=credential)

        _, ws_id = await fabric_client.resolve_workspace_name_and_id(ws)

        response = await fabric_client.set_item_permissions(
            workspace_id=ws_id,
            item_id=item_id,
            assignments=assignments,
            principal_scope=scope,
        )

        return {
            "workspace": ws,
            "itemId": item_id,
            "result": response,
        }
    except Exception as exc:
        logger.error("Failed to set permissions for %s: %s", item_id, exc)
        return {"error": str(exc)}


