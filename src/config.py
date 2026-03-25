from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(
    name="Clint_MCP",
    instructions=(
        "MCP Server for the Clint CRM platform. Manage the full sales pipeline via API.\n\n"
        "CONTACTS: List (filter by name, phone, email, tags, origin), get by UUID, create, update, "
        "and delete contacts. Manage contact tags (add/remove).\n\n"
        "DEALS: List (filter by creation/update date, assigned user, status OPEN/WON/LOST, stage, "
        "tags, won/lost dates), get by ID, create, update (including stage and status changes), "
        "and delete deals.\n\n"
        "TAGS: List, get, create (with custom color), and delete tags.\n\n"
        "CRM CONFIGURATION: List origins by group, query users, groups, organizations "
        "(with update support), lost status reasons, and account custom fields.\n\n"
        "Contacts and deals support custom_fields. Always call list_fields first to discover "
        "available fields before creating or updating records. When looking up a specific contact "
        "or deal, prefer using list filters (name, phone, email) rather than requiring an ID from the user."
    ),
    mask_error_details=False,
)
