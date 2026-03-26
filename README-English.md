# MCP Clint CRM

MCP (Model Context Protocol) server for integration with [Clint CRM](https://clint.digital/). Manage contacts, deals, tags, organizations, and all your CRM configuration directly through MCP-compatible AI assistants.

> **[Versão em Português disponível aqui](README.md)**

---

> **Disclaimer:** This is a **community-maintained open source** project. It is **not an official tool** from Clint CRM. Use at your own risk. Refer to the [official Clint CRM API documentation](https://clint-api.readme.io/reference/get_contacts) for API information.

---

## Prerequisites

- **Clint CRM Elite Plan** — API access requires an active Elite plan on your Clint account.
- **Clint CRM API Key** — Access key generated in your Clint account for API authentication.
- **Python 3.14+** — The project uses modern Python features.
- **UV** — Python package and virtual environment manager. [Install UV](https://docs.astral.sh/uv/getting-started/installation/).

### Useful Links

- [Clint CRM API Documentation](https://clint-api.readme.io/reference/get_contacts)
- [Clint CRM](https://clint.digital/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mcp-clint-crm.git
cd mcp-clint-crm
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
# Required — your Clint CRM API key
CLINT_API_KEY=your_api_key_here

# Optional — only needed for HTTP mode (see "HTTP Deployment" section)
CLINT_MCP_TRANSPORT=stdio
CLINT_MCP_HOST=0.0.0.0
CLINT_MCP_PORT=8001
```

| Variable | Required | Description |
|----------|----------|-------------|
| `CLINT_API_KEY` | Yes | Clint CRM API key (Elite plan) |
| `CLINT_MCP_TRANSPORT` | No | Server transport: `stdio` (default) or `streamable-http` |
| `CLINT_MCP_HOST` | No | HTTP server host (default: `0.0.0.0`) |
| `CLINT_MCP_PORT` | No | HTTP server port (default: `8001`) |

### 3. Install dependencies

```bash
uv sync
```

### 4. Run the server (stdio mode)

```bash
uv run src/server.py
```

---

## stdio Configuration (Claude Desktop, Cursor, etc.)

To use the MCP server with AI assistants that support the MCP protocol via **stdio**, add the following configuration to your MCP client's configuration file.

### Claude Desktop

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clint-crm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-clint-crm",
        "src/server.py"
      ],
      "env": {
        "CLINT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Cursor

In Cursor's MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "clint-crm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-clint-crm",
        "src/server.py"
      ],
      "env": {
        "CLINT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add clint-crm -- uv run --directory /absolute/path/to/mcp-clint-crm src/server.py
```

> **Note:** Replace `/absolute/path/to/mcp-clint-crm` with the actual project path on your system. The `CLINT_API_KEY` variable can be defined in the project's `.env` file or directly in the MCP client's `env` configuration.

---

## HTTP Deployment (Remote server / VPS / Cloud)

To make the MCP server available over the network (e.g., for use with Claude.ai, Cowork, ChatGPT), the server runs in HTTP mode with Streamable HTTP transport.

### Option 1: Docker (recommended)

```bash
git clone https://github.com/your-username/mcp-clint-crm.git
cd mcp-clint-crm
```

Configure `.env`:

```env
CLINT_API_KEY=your_api_key_here
```

Start the container:

```bash
docker compose up -d
```

The server will be available at `http://your-server:8001/mcp` with automatic health check at `/health`.

### Option 2: Uvicorn directly

```bash
cd mcp-clint-crm && uv sync
CLINT_MCP_TRANSPORT=streamable-http uv run uvicorn server:app --host 0.0.0.0 --port 8001 --app-dir src
```

### Option 3: VPS with PM2

```bash
cd mcp-clint-crm && uv sync
pm2 start "uv run uvicorn server:app --host 0.0.0.0 --port 8001 --app-dir src" --name clint-mcp
```

### MCP client configuration (HTTP)

After deploying, configure your MCP client with the server URL.

**Claude.ai / Cowork:**

Add as a custom connector in the UI, or in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clint-crm": {
      "type": "http",
      "url": "https://your-server.com/mcp"
    }
  }
}
```

**ChatGPT / Codex:**

```json
{
  "mcpServers": {
    "clint-crm": {
      "url": "https://your-server.com/mcp"
    }
  }
}
```

> **Important:** In production, use HTTPS (TLS) with a reverse proxy (Nginx, Caddy, etc.) in front of the MCP server. The server itself does not handle TLS termination.

---

## Available Tools

The server exposes **27 tools** organized by domain. Each tool is annotated with safety metadata (read-only / destructive) so the AI assistant requests confirmation before executing dangerous actions.

### Overview

| Domain | Tools | Operations |
|--------|-------|------------|
| **Contacts** | 7 | List, get, create, update, delete, add/remove tags |
| **Deals** | 5 | List, get, create, update, delete |
| **Tags** | 4 | List, get, create, delete |
| **Organizations** | 2 | Get, update |
| **Origins** | 2 | List, get |
| **Groups** | 2 | List, get |
| **Users** | 2 | List, get |
| **Lost Status** | 2 | List, get |
| **Account** | 1 | List custom fields |

---

### Contacts

#### `list_contacts`
List all CRM contacts with optional filters. Returns up to 1000 contacts per call with pagination support.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |
| `name` | `str` | Filter by contact name |
| `phone` | `str` | Filter by phone (without country code) |
| `email` | `str` | Filter by email |
| `tag_names` | `str` | Filter by tags (comma-separated) |
| `origin_id` | `str` | Filter by origin (use `list_origins` to get IDs) |

#### `get_contact`
Returns full details of a contact by UUID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | `str` | Contact ID (get via `list_contacts`) |

#### `create_contact`
Creates a new contact in the CRM.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Contact name (**required**) |
| `ddi` | `str` | Country dialing code |
| `phone` | `str` | Phone number |
| `email` | `str` | Email address |
| `username` | `str` | Username |
| `fields` | `dict \| str` | Custom fields (JSON). Use `list_fields` to discover available fields |

#### `update_contact`
Updates an existing contact. Send only the fields you want to change.

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | `str` | Contact ID (**required**) |
| `name` | `str` | New name |
| `ddi` | `str` | New DDI |
| `phone` | `str` | New phone |
| `email` | `str` | New email |
| `username` | `str` | New username |
| `fields` | `dict \| str` | Custom fields (JSON) |

#### `delete_contact`
Permanently deletes a contact. **Destructive action** — requires confirmation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | `str` | Contact ID (**required**) |

#### `add_tags`
Adds one or more tags to a contact.

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | `str` | Contact ID (**required**) |
| `tag_names` | `list[str]` | List of tag names to add |

#### `remove_tags`
Removes a tag from a contact. **Destructive action** — requires confirmation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | `str` | Contact ID (**required**) |
| `tag_name` | `str` | Tag name to remove |

---

### Deals

#### `list_deals`
List deals with advanced filters by date, status, user, and tags. Returns up to 1000 deals per call.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |
| `created_at_start` | `str` | Creation start date (ISO 8601) |
| `created_at_end` | `str` | Creation end date (ISO 8601) |
| `updated_at_start` | `str` | Update start date (ISO 8601) |
| `updated_at_end` | `str` | Update end date (ISO 8601) |
| `user_email` | `str` | Filter by assigned user email |
| `phone` | `str` | Filter by phone |
| `email` | `str` | Filter by email |
| `tag_names` | `str` | Filter by tags (comma-separated) |
| `status` | `str` | Status: `OPEN`, `WON`, or `LOST` (default: `OPEN`) |
| `won_at_start` | `str` | Won start date (ISO 8601) |
| `won_at_end` | `str` | Won end date (ISO 8601) |
| `lost_at_start` | `str` | Lost start date (ISO 8601) |
| `lost_at_end` | `str` | Lost end date (ISO 8601) |
| `stage_id` | `str` | Filter by pipeline stage |

#### `get_deal`
Returns full details of a deal by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Deal ID (get via `list_deals`) |

#### `create_deal`
Creates a new deal in the CRM. Requires an origin.

| Parameter | Type | Description |
|-----------|------|-------------|
| `origin_id` | `str` | Origin ID (**required**, use `list_origins`) |
| `name` | `str` | Contact name |
| `phone` | `str` | Phone number |
| `email` | `str` | Email address |
| `username` | `str` | Username |
| `value` | `float` | Deal value |
| `stage_id` | `str` | Pipeline stage ID |
| `user_id` | `str` | Assigned user ID |
| `contact_id` | `str` | Existing contact ID |
| `fields` | `dict \| str` | Custom fields (JSON) |

#### `update_deal`
Updates an existing deal, including status and pipeline stage changes.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Deal ID (**required**) |
| `name` | `str` | New name |
| `phone` | `str` | New phone |
| `email` | `str` | New email |
| `value` | `float` | New value |
| `stage_id` | `str` | New pipeline stage |
| `status` | `str` | New status: `OPEN`, `WON`, or `LOST` |
| `user_id` | `str` | New assigned user |
| `origin_id` | `str` | New origin |
| `fields` | `dict \| str` | Custom fields (JSON) |

#### `remove_deal`
Permanently deletes a deal. **Destructive action** — requires confirmation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Deal ID (**required**) |

---

### Tags

#### `list_tags`
List all tags with optional name filtering.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |
| `name` | `str` | Filter by tag name |

#### `get_tag`
Returns tag details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Tag ID (get via `list_tags`) |

#### `create_tag`
Creates a new tag with a name and color.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Tag name (**required**) |
| `color` | `str` | Hex color code (default: `#f44336`) |

**Available colors:**

| Color | Code |
|-------|------|
| Red | `#f44336` |
| Pink | `#e91e63` |
| Purple | `#9c27b0` |
| Deep Purple | `#673ab7` |
| Blue | `#2196f3` |
| Orange | `#faa200` |
| Brown | `#795548` |
| Blue Grey | `#607d8b` |

#### `delete_tag`
Permanently deletes a tag. **Destructive action** — requires confirmation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Tag ID (**required**) |

---

### Organizations

#### `get_organization`
Returns organization details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Organization ID |

#### `update_organization`
Updates an existing organization. **Destructive action** — requires confirmation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Organization ID (**required**) |
| `name` | `str` | New name |
| `custom_fields` | `dict \| str` | Custom fields (JSON) |

---

### Origins

#### `list_origins`
List origins filtered by group. Each origin contains its pipeline stages.

| Parameter | Type | Description |
|-----------|------|-------------|
| `group_id` | `str` | Group ID (**required**, use `list_groups`) |
| `offset` | `int` | Pagination offset (default: 0) |

#### `get_origin`
Returns origin details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Origin ID (get via `list_origins`) |

---

### Groups

#### `list_groups`
List all available groups in the CRM.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |

#### `get_group`
Returns group details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Group ID (get via `list_groups`) |

---

### Users

#### `list_users`
List all system users.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |

#### `get_user`
Returns user details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | User ID (get via `list_users`) |

---

### Lost Status

#### `list_lost_status`
List all deal loss reasons.

| Parameter | Type | Description |
|-----------|------|-------------|
| `offset` | `int` | Pagination offset (default: 0) |

#### `get_lost_status`
Returns lost status details by ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Status ID (get via `list_lost_status`) |

---

### Account

#### `list_fields`
List all custom fields configured in the account. **Use this tool before creating or updating contacts and deals** to discover available fields and their types.

No additional parameters required.

---

## Custom Fields

Contacts, deals, and organizations support custom fields. The recommended workflow is:

1. Call `list_fields` to discover available fields, their key names, types, and options.
2. When creating or updating a record, pass the fields in the `fields` parameter as a JSON object:

```json
{
  "custom_field_1": "value",
  "custom_field_2": 123
}
```

Fields can be passed as a Python `dict` or as a valid JSON string.

---

## Pagination

All list operations return up to **1000 records** per call. To get more results, use the `offset` parameter:

- First call: `offset=0` (default)
- Second call: `offset=1000`
- Third call: `offset=2000`
- And so on...

The server returns the total available records and suggests the next offset when more data is available.

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.14+ | Main language |
| FastMCP | 3.1.1+ | MCP framework |
| httpx | 0.28.1+ | Async HTTP client |
| Pydantic | 2.12.5+ | Data validation and models |
| UV | - | Package manager |
| Docker | - | Containerization (optional) |

---

## Contributing

Contributions are welcome! Feel free to open issues and pull requests.

---

## License

This project is open source. Check the license file for more details.

---

<sub>Developed by the community. Not affiliated with Clint CRM.</sub>
