from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key, parse_fields
from formatters import format_contacts
from models import Contact


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_contacts(
    offset: int = 0,
    name: str | None = None,
    phone: str | None = None,
    tag_names: str | None = None,
    email: str | None = None,
    origin_id: str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    List all contacts from the CRM.
    Optionally filter by name, email, phone (without country code), tag_names,
    or origin_id (use list_origins to find valid origin IDs).
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    params = {}
    if name:
        params["name"] = name
    if email:
        params["email"] = email
    if phone:
        params["phone"] = phone
    if tag_names:
        params["tag_names"] = tag_names
    if origin_id:
        params["origin_id"] = origin_id

    client = ClintClient(api_key)
    try:
        result = await client.get_list("/contacts", Contact, params=params, offset=offset)
        return format_contacts(
            result.response.data, result.response.totalCount, result.offset
        )
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_contact(uuid: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Get full details of a single contact by UUID.
    Use list_contacts first to find the contact ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/contacts/{uuid}", Contact)
        return format_contacts([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    timeout=15.0,
)
async def create_contact(
    name: str,
    ddi: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    username: str | None = None,
    fields: dict | str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Creates a contact.
    fields: custom fields as a JSON object (e.g. {"field_key": "value"}).
    Call list_fields first to discover available field keys.
    """
    fields = parse_fields(fields)
    body = {"name": name}
    if ddi:
        body["ddi"] = ddi
    if phone:
        body["phone"] = phone
    if email:
        body["email"] = email
    if username:
        body["username"] = username
    if fields:
        body["fields"] = fields

    client = ClintClient(api_key)
    try:
        result = await client.post("/contacts", Contact, data=body)
        return format_contacts([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def update_contact(
    uuid: str,
    name: str | None = None,
    ddi: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    username: str | None = None,
    fields: dict | str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Update contact by its ID.
    Use list_contacts first to find the contact ID.
    fields: custom fields as a JSON object (e.g. {"field_key": "value"}).
    Call list_fields first to discover available field keys.
    """
    fields = parse_fields(fields)
    body = {}
    if name is not None:
        body["name"] = name
    if ddi is not None:
        body["ddi"] = ddi
    if phone is not None:
        body["phone"] = phone
    if email is not None:
        body["email"] = email
    if username is not None:
        body["username"] = username
    if fields is not None:
        body["fields"] = fields

    if not body:
        return "No fields to update were provided."

    client = ClintClient(api_key)
    try:
        result = await client.post(f"/contacts/{uuid}", Contact, data=body)
        return format_contacts([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def delete_contact(uuid: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    WARNING: This is a destructive action, ask user permission to execute.
    Deletes a contact by its ID.
    Use list_contacts first to find the contact ID.
    """
    client = ClintClient(api_key)
    try:
        await client.delete(f"/contacts/{uuid}")
        return f"Contact {uuid} deleted successfully."
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    timeout=15.0,
)
async def add_tags(
    uuid: str,
    tag_names: list[str],
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Add tags to a single contact.
    Use list_contacts first to find the contact ID.
    Use list_tags to find tags IDs or names.
    """
    client = ClintClient(api_key)
    try:
        await client.post(f"/contacts/{uuid}/tags", data=tag_names)
        return f"Tags added to contact {uuid}."
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def remove_tags(
    uuid: str,
    tag_name: str,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    WARNING: This is a destructive action, ask user permission to execute.
    Remove a tag from a single contact.
    Use list_contacts first to find the contact ID.
    Use list_tags to find tag names.
    """
    client = ClintClient(api_key)
    try:
        await client.delete(f"/contacts/{uuid}/tags", data={"tag_name": tag_name})
        return f"Tag '{tag_name}' removed from contact {uuid}."
    finally:
        await client.close()
