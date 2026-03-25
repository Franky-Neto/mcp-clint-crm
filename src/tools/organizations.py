from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key, parse_fields
from formatters import format_organization
from models import Organization


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_organization(
    id: str, api_key: str = Depends(get_clint_api_key)
) -> str:
    """
    Retrieve details of a single organization by ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/organizations/{id}", Organization)
        return format_organization(result.data)
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def update_organization(
    id: str,
    name: str | None = None,
    custom_fields: dict | str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Update an existing organization.
    Use get_organization first to check current data.
    custom_fields: custom fields as a JSON object (e.g. {"field_key": "value"}).
    """
    custom_fields = parse_fields(custom_fields)
    body = {}
    if name is not None:
        body["name"] = name
    if custom_fields is not None:
        body["custom_fields"] = custom_fields

    if not body:
        return "No fields to update were provided."

    client = ClintClient(api_key)
    try:
        result = await client.post(f"/organizations/{id}", Organization, data=body)
        return format_organization(result.data)
    finally:
        await client.close()
