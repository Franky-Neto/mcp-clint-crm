from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from config import mcp, TRANSPORT, HOST, PORT  # noqa: F401
from tools import account, contacts, tags, deals, groups, organizations, origins, status, users  # noqa: F401


# --- Health check ----------------------------------------------------

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "clint-mcp"})


# --- ASGI app (HTTP mode) -------------------------------------------

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["mcp-protocol-version", "mcp-session-id", "Authorization", "Content-Type"],
        expose_headers=["mcp-session-id"],
    )
]

app = mcp.http_app(transport="streamable-http", middleware=middleware)


# --- Entrypoint ------------------------------------------------------

if __name__ == "__main__":
    if TRANSPORT == "stdio":
        mcp.run()
    else:
        mcp.run(transport=TRANSPORT, host=HOST, port=PORT)
