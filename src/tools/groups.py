from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_groups
from models import Group


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_groups(
    offset: int = 0,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of all groups.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    client = ClintClient(api_key)
    try:
        result = await client.get_list("/groups", Group, offset=offset)
        return format_groups(result.response.data, result.response.totalCount, result.offset)
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_group(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Retrieve a single group by ID.
    Use list_groups to find the group ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/groups/{id}", Group)
        return format_groups([result.data])
    finally:
        await client.close()
