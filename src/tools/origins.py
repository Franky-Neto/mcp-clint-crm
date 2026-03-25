from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_origins
from models import Origin


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_origins(
    group_id: str,
    offset: int = 0,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of origins filtered by group.
    group_id is required — use list_groups to find valid group IDs.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    params = {"group_id": group_id}
    client = ClintClient(api_key)
    try:
        result = await client.get_list("/origins", Origin, params=params, offset=offset)
        return format_origins(
            result.response.data, result.response.totalCount, result.offset
        )
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_origin(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Retrieve a single origin by ID.
    Use list_origins to find the origin ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/origins/{id}", Origin)
        return format_origins([result.data])
    finally:
        await client.close()
