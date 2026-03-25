import json
import os

from fastmcp.exceptions import ToolError


async def get_clint_api_key() -> str:
    """Resolve the Clint API key. Hidden from tool schema via Depends()."""

    key = os.environ.get("CLINT_API_KEY", "")
    if key:
        return key

    raise ToolError(
        "Clint API key not configured. "
        "Set CLINT_API_KEY env var."
    )


def parse_fields(value: dict | str | None) -> dict | None:
    """Parse fields that may arrive as a JSON string from MCP clients."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ToolError("fields must be a JSON object, not a list or scalar.")
        return parsed
    except json.JSONDecodeError as exc:
        raise ToolError(f"Invalid JSON in fields: {exc}") from exc
