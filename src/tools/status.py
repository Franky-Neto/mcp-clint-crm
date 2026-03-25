from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_lost_status
from models import LostStatus


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_lost_status(
    offset: int = 0,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of all lost status reasons.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    client = ClintClient(api_key)
    try:
        result = await client.get_list("/lost-status", LostStatus, offset=offset)
        return format_lost_status(
            result.response.data, result.response.totalCount, result.offset
        )
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_lost_status(
    id: str, api_key: str = Depends(get_clint_api_key)
) -> str:
    """
    Retrieve a single lost status by ID.
    Use list_lost_status to find the status ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/lost-status/{id}", LostStatus)
        return format_lost_status([result.data])
    finally:
        await client.close()
