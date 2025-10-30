import json
from typing import Any, Dict, Optional

import requests

from helpers.logging_config import get_logger
from helpers.utils.authentication import get_azure_credentials
from helpers.utils.context import mcp, __ctx_cache
from mcp.server.fastmcp import Context


logger = get_logger(__name__)


def _graph_headers(ctx: Context) -> Dict[str, str]:
    credential = get_azure_credentials(ctx.client_id, __ctx_cache)
    token = credential.get_token("https://graph.microsoft.com/.default")
    return {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _graph_request(
    ctx: Context,
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    headers = _graph_headers(ctx)
    response = requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code >= 400:
        logger.error(
            "Graph API error %s: %s", response.status_code, response.text[:500]
        )
        return {
            "status": response.status_code,
            "error": response.text,
        }

    if not response.text:
        return {"status": response.status_code}

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"status": response.status_code, "raw": response.text}


@mcp.tool()
async def graph_user(email: str, ctx: Context) -> Dict[str, Any]:
    """Query Azure AD user profile details via Microsoft Graph."""

    try:
        url = f"https://graph.microsoft.com/v1.0/users/{email}"
        return _graph_request(ctx, "get", url)
    except Exception as exc:
        logger.error("Error retrieving Graph user: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def graph_mail(
    to: str,
    subject: str,
    body: str,
    ctx: Context,
) -> Dict[str, Any]:
    """Send mail via Microsoft Graph on behalf of the current identity."""

    try:
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body,
                },
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
            "saveToSentItems": True,
        }
        return _graph_request(ctx, "post", url, payload)
    except Exception as exc:
        logger.error("Error sending Graph mail: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def graph_teams_message(
    team_id: str,
    channel_id: str,
    text: str,
    ctx: Context,
) -> Dict[str, Any]:
    """Post a message to a Teams channel via Microsoft Graph."""

    try:
        url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
        payload = {
            "body": {
                "contentType": "html",
                "content": text,
            }
        }
        return _graph_request(ctx, "post", url, payload)
    except Exception as exc:
        logger.error("Error posting Teams message: %s", exc)
        return {"error": str(exc)}


@mcp.tool()
async def graph_drive(
    drive_id: str,
    path: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """List files in a OneDrive or SharePoint drive via Microsoft Graph."""

    try:
        if ctx is None:
            raise ValueError("Context (ctx) must be provided.")

        normalised_path = (path or "").strip("/")
        if normalised_path:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{normalised_path}:/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"

        return _graph_request(ctx, "get", url)
    except Exception as exc:
        logger.error("Error listing drive items: %s", exc)
        return {"error": str(exc)}



