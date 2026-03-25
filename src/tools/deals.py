from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key, parse_fields
from formatters import format_deals
from models import Deal


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_deals(
    offset: int = 0,
    created_at_start: str | None = None,
    created_at_end: str | None = None,
    updated_at_start: str | None = None,
    updated_at_end: str | None = None,
    user_email: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    tag_names: str | None = None,
    status: str | None = None,
    won_at_start: str | None = None,
    won_at_end: str | None = None,
    lost_at_start: str | None = None,
    lost_at_end: str | None = None,
    stage_id: str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of deals.
    Optionally filter by date ranges (ISO 8601), user_email, phone, email,
    tag_names (comma-separated), status (OPEN, WON, LOST), or stage_id.
    Defaults to status=OPEN if not specified.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    params = {}
    if created_at_start:
        params["created_at_start"] = created_at_start
    if created_at_end:
        params["created_at_end"] = created_at_end
    if updated_at_start:
        params["updated_at_start"] = updated_at_start
    if updated_at_end:
        params["updated_at_end"] = updated_at_end
    if user_email:
        params["user_email"] = user_email
    if phone:
        params["phone"] = phone
    if email:
        params["email"] = email
    if tag_names:
        params["tag_names"] = tag_names
    if status:
        params["status"] = status
    if won_at_start:
        params["won_at_start"] = won_at_start
    if won_at_end:
        params["won_at_end"] = won_at_end
    if lost_at_start:
        params["lost_at_start"] = lost_at_start
    if lost_at_end:
        params["lost_at_end"] = lost_at_end
    if stage_id:
        params["stage_id"] = stage_id

    client = ClintClient(api_key)
    try:
        result = await client.get_list("/deals", Deal, params=params, offset=offset)
        return format_deals(
            result.response.data, result.response.totalCount, result.offset
        )
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    timeout=15.0,
)
async def create_deal(
    origin_id: str,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    username: str | None = None,
    value: float | None = None,
    stage_id: str | None = None,
    user_id: str | None = None,
    contact_id: str | None = None,
    fields: dict | str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Create a new deal in the CRM.
    origin_id is required — use list_origins to find valid origin IDs.
    fields: custom fields as a JSON object (e.g. {"field_key": "value"}).
    Call list_fields first to discover available field keys.
    """
    fields = parse_fields(fields)
    body = {"origin_id": origin_id}
    if name:
        body["name"] = name
    if phone:
        body["phone"] = phone
    if email:
        body["email"] = email
    if username:
        body["username"] = username
    if value is not None:
        body["value"] = value
    if stage_id:
        body["stage_id"] = stage_id
    if user_id:
        body["user_id"] = user_id
    if contact_id:
        body["contact_id"] = contact_id
    if fields:
        body["fields"] = fields

    client = ClintClient(api_key)
    try:
        result = await client.post("/deals", Deal, data=body)
        return format_deals([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_deal(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Retrieve a single deal by ID.
    Use list_deals to find the deal ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/deals/{id}", Deal)
        return format_deals([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def update_deal(
    id: str,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    value: float | None = None,
    stage_id: str | None = None,
    status: str | None = None,
    user_id: str | None = None,
    origin_id: str | None = None,
    fields: dict | str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Update an existing deal.
    Use list_deals or get_deal to find the deal ID.
    Status options: OPEN, WON, LOST.
    fields: custom fields as a JSON object (e.g. {"field_key": "value"}).
    Call list_fields first to discover available field keys.
    """
    fields = parse_fields(fields)
    body = {}
    if name is not None:
        body["name"] = name
    if phone is not None:
        body["phone"] = phone
    if email is not None:
        body["email"] = email
    if value is not None:
        body["value"] = value
    if stage_id is not None:
        body["stage_id"] = stage_id
    if status is not None:
        body["status"] = status
    if user_id is not None:
        body["user_id"] = user_id
    if origin_id is not None:
        body["origin_id"] = origin_id
    if fields is not None:
        body["fields"] = fields

    if not body:
        return "No fields to update were provided."

    client = ClintClient(api_key)
    try:
        await client.post(f"/deals/{id}", data=body)
        result = await client.get(f"/deals/{id}", Deal)
        return format_deals([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def remove_deal(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    WARNING: This is a destructive action, ask user permission to execute.
    Remove a deal permanently by ID.
    Use list_deals or get_deal to find the deal ID.
    """
    client = ClintClient(api_key)
    try:
        await client.delete(f"/deals/{id}")
        return f"Deal {id} deleted successfully."
    finally:
        await client.close()
