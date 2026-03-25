from fastmcp.dependencies import Depends
from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from client import ClintClient
from config import mcp
from dependencies import get_clint_api_key
from formatters import format_fields
from models import AccountFields


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False},
    timeout=15.0,
)
async def list_fields(api_key: str = Depends(get_clint_api_key)) -> str:
    """
    Get all custom fields available in the account.
    Use this to discover field names before creating or updating contacts and deals.
    """
    client = ClintClient(api_key)
    try:
        raw = await client.get("/account/fields")
        account = AccountFields.model_validate(raw.get("data", {}))
        return format_fields(account)
    except (ValidationError, KeyError, TypeError) as exc:
        raise ToolError(
            f"Unexpected response format from /account/fields: {exc}"
        ) from exc
    finally:
        await client.close()
