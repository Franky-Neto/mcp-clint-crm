from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_tags
from models import Tag


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_tags(
    offset: int = 0,
    name: str | None = None,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of tags.
    Optionally filter by name.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    params = {}
    if name:
        params["name"] = name

    client = ClintClient(api_key)
    try:
        result = await client.get_list("/tags", Tag, params=params, offset=offset)
        return format_tags(result.response.data, result.response.totalCount, result.offset)
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_tag(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Retrieve a single tag by ID.
    Use list_tags to find the tag ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/tags/{id}", Tag)
        return format_tags([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    timeout=15.0,
)
async def create_tag(
    name: str,
    color: str = "#f44336",
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Create a new tag.
    Available colors: #f44336, #e91e63, #9c27b0, #673ab7, #2196f3, #faa200, #795548, #607d8b
    """
    body = {"name": name, "color": color}
    client = ClintClient(api_key)
    try:
        result = await client.post("/tags/", Tag, data=body)
        return format_tags([result.data])
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True},
    timeout=15.0,
)
async def delete_tag(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    WARNING: This is a destructive action, ask user permission to execute.
    Remove a single tag by ID.
    Use list_tags to find the tag ID.
    """
    client = ClintClient(api_key)
    try:
        await client.delete(f"/tags/{id}")
        return f"Tag {id} deleted successfully."
    finally:
        await client.close()
