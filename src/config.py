import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken
from fastmcp.server.auth.providers.google import GoogleProvider, GoogleTokenVerifier

load_dotenv()

logger = logging.getLogger(__name__)

# --- Settings --------------------------------------------------------

TRANSPORT = os.environ.get("CLINT_MCP_TRANSPORT", "stdio")
HOST = os.environ.get("CLINT_MCP_HOST", "0.0.0.0")
PORT = int(os.environ.get("CLINT_MCP_PORT", "8001"))

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_BASE_URL = os.environ.get("GOOGLE_AUTH_BASE_URL", "http://localhost:8001")

# Access control
RESTRICT_BY_EMAIL = os.environ.get("CLINT_MCP_RESTRICT_BY_EMAIL", "false").lower() == "true"
RESTRICT_BY_DOMAIN = os.environ.get("CLINT_MCP_RESTRICT_BY_DOMAIN", "false").lower() == "true"
ALLOWED_EMAILS = [
    e.strip() for e in os.environ.get("CLINT_MCP_ALLOWED_EMAILS", "").split(",") if e.strip()
]
ALLOWED_DOMAINS = [
    d.strip() for d in os.environ.get("CLINT_MCP_ALLOWED_DOMAINS", "").split(",") if d.strip()
]


# --- Auth ------------------------------------------------------------

class RestrictedGoogleVerifier(GoogleTokenVerifier):
    """Google token verifier with email/domain allowlist."""

    def __init__(self, allowed_emails: list[str], allowed_domains: list[str],
                 restrict_by_email: bool, restrict_by_domain: bool, **kwargs):
        super().__init__(**kwargs)
        self._allowed_emails = [e.lower() for e in allowed_emails]
        self._allowed_domains = [d.lower() for d in allowed_domains]
        self._restrict_by_email = restrict_by_email
        self._restrict_by_domain = restrict_by_domain

    async def verify_token(self, token: str) -> AccessToken | None:
        access_token = await super().verify_token(token)
        if access_token is None:
            return None

        # If no restrictions enabled, allow all authenticated users
        if not self._restrict_by_email and not self._restrict_by_domain:
            return access_token

        email = (access_token.claims or {}).get("email", "")
        if not email:
            logger.warning("Google token has no email claim — access denied")
            return None

        email_lower = email.lower()
        domain = email_lower.split("@")[-1]

        if self._restrict_by_email and email_lower in self._allowed_emails:
            return access_token

        if self._restrict_by_domain and domain in self._allowed_domains:
            return access_token

        logger.warning("Access denied for %s — not in allowlist", email)
        return None


auth = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    verifier = RestrictedGoogleVerifier(
        allowed_emails=ALLOWED_EMAILS,
        allowed_domains=ALLOWED_DOMAINS,
        restrict_by_email=RESTRICT_BY_EMAIL,
        restrict_by_domain=RESTRICT_BY_DOMAIN,
        required_scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
    )
    auth = GoogleProvider(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        base_url=GOOGLE_AUTH_BASE_URL,
        required_scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
    )
    # Replace the default verifier with our restricted one
    auth._token_validator = verifier

# --- MCP instance ----------------------------------------------------

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
    auth=auth,
)
