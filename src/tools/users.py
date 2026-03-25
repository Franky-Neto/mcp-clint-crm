from fastmcp.dependencies import Depends

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_users
from models import User


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=30.0,
)
async def list_users(
    offset: int = 0,
    api_key: str = Depends(get_clint_api_key),
) -> str:
    """
    Retrieve a list of all users.
    Returns up to 1000 per call. Use offset to paginate (e.g., offset=1000 for next batch).
    """
    client = ClintClient(api_key)
    try:
        result = await client.get_list("/users", User, offset=offset)
        return format_users(result.response.data, result.response.totalCount, result.offset)
    finally:
        await client.close()


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def get_user(id: str, api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Retrieve a single user by ID.
    Use list_users to find the user ID.
    """
    client = ClintClient(api_key)
    try:
        result = await client.get(f"/users/{id}", User)
        return format_users([result.data])
    finally:
        await client.close()
