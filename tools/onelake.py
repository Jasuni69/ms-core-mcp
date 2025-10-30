import base64
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context

from helpers.clients import FabricApiClient, OneLakeClient
from helpers.logging_config import get_logger
from helpers.utils.authentication import get_azure_credentials
from helpers.utils.context import mcp, __ctx_cache


logger = get_logger(__name__)


async def _resolve_lakehouse_context(
    ctx: Context,
    workspace: Optional[str],
    lakehouse: str,
):
    if ctx is None:
        raise ValueError("Context is required for OneLake operations.")

    ws = workspace or __ctx_cache.get(f"{ctx.client_id}_workspace")
    if not ws:
        raise ValueError(
            "Workspace not set. Provide a workspace value or call set_workspace first."
        )

    credential = get_azure_credentials(ctx.client_id, __ctx_cache)
    fabric_client = FabricApiClient(credential=credential)

    workspace_name, workspace_id = await fabric_client.resolve_workspace_name_and_id(ws)
    _, lakehouse_id = await fabric_client.resolve_item_name_and_id(
        item=lakehouse,
        type="Lakehouse",
        workspace=workspace_id,
    )

    logger.debug(
        "Resolved workspace '%s' (%s) and lakehouse '%s' (%s)",
        workspace_name,
        workspace_id,
        lakehouse,
        lakehouse_id,
    )

    return credential, workspace_id, lakehouse_id


@mcp.tool()
async def onelake_ls(
    lakehouse: str,
    path: Optional[str] = None,
    workspace: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """List files and folders within a OneLake lakehouse path."""

    try:
        credential, workspace_id, lakehouse_id = await _resolve_lakehouse_context(
            ctx, workspace, lakehouse
        )
        client = OneLakeClient(credential)
        entries = await client.list_directory(workspace_id, lakehouse_id, path)
        return {
            "workspaceId": workspace_id,
            "lakehouseId": lakehouse_id,
            "path": path or "Files",
            "entries": entries,
        }
    except Exception as exc:
        logger.error("OneLake list failed: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def onelake_read(
    lakehouse: str,
    path: str,
    workspace: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Read file contents from OneLake."""

    try:
        credential, workspace_id, lakehouse_id = await _resolve_lakehouse_context(
            ctx, workspace, lakehouse
        )
        client = OneLakeClient(credential)
        return await client.read_file(workspace_id, lakehouse_id, path)
    except Exception as exc:
        logger.error("OneLake read failed: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def onelake_write(
    lakehouse: str,
    path: str,
    content: str,
    workspace: Optional[str] = None,
    overwrite: bool = True,
    encoding: str = "utf-8",
    is_base64: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Write text or base64 content to OneLake."""

    try:
        credential, workspace_id, lakehouse_id = await _resolve_lakehouse_context(
            ctx, workspace, lakehouse
        )

        if is_base64:
            data = base64.b64decode(content)
        else:
            data = content.encode(encoding)

        client = OneLakeClient(credential)
        result = await client.write_file(
            workspace_id, lakehouse_id, path, data, overwrite=overwrite
        )
        result["encoding"] = "base64" if is_base64 else encoding
        return result
    except Exception as exc:
        logger.error("OneLake write failed: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def onelake_rm(
    lakehouse: str,
    path: str,
    workspace: Optional[str] = None,
    recursive: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Delete a file or directory from OneLake."""

    try:
        credential, workspace_id, lakehouse_id = await _resolve_lakehouse_context(
            ctx, workspace, lakehouse
        )
        client = OneLakeClient(credential)
        return await client.delete_path(
            workspace_id, lakehouse_id, path, recursive=recursive
        )
    except Exception as exc:
        logger.error("OneLake delete failed: %s", exc)
        return {"error": str(exc)}


