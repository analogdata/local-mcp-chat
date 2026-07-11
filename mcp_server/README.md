# Books ERP MCP Server

An MCP (Model Context Protocol) server that exposes all Books ERP CRUD operations as tools, allowing LLM clients like **LM Studio** (with Qwen, Gemma3, etc.) to manage the book inventory through natural language.

The MCP server communicates with the **Books ERP REST API** over HTTP using the configured API host address and Bearer token for authentication.

## Available Tools

| Tool | Description |
|------|-------------|
| `create_book` | Add a new book to the inventory |
| `list_books` | List books with filtering (genre, author, price range, in-stock) and pagination |
| `get_book` | Retrieve a single book by ID |
| `search_books` | Search books by title, author, or description |
| `get_book_stats` | Get aggregate inventory statistics (total books, stock, value, by genre) |
| `update_book` | Partially update a book (only provided fields are changed) |
| `delete_book` | Delete a book from the inventory |

## How It Works

The MCP server acts as an HTTP client that calls the Books ERP REST API. It requires the REST API server to be running. The server runs over **stdio transport**, which is the standard for local MCP servers.

```
LLM Client (LM Studio)  →  MCP Server (stdio)  →  REST API (HTTP + Bearer Auth)  →  SQLite
```

## Prerequisites

The Books ERP REST API must be running:

```bash
export BOOKS_API_TOKEN="secret-token-123"
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

## Running the MCP Server

### Standalone

```bash
# From the project root
export BOOKS_API_HOST="http://127.0.0.1:8000"
export BOOKS_API_TOKEN="secret-token-123"
uv run python -m mcp_server.main
```

The server listens on stdin/stdout for MCP protocol messages.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOOKS_API_HOST` | `http://127.0.0.1:8000` | Base URL of the Books ERP REST API |
| `BOOKS_API_TOKEN` | `secret-token-123` | Bearer token for API authentication |

### Configuration for LM Studio

In LM Studio's MCP settings, add the following server configuration:

#### Option 1: Using `mcp_config.json`

Copy the contents of `mcp_server/mcp_config.json` into LM Studio's MCP server configuration:

```json
{
  "mcpServers": {
    "books-erp": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.main"],
      "cwd": "/Users/rajathkumar/localmcpchat",
      "env": {
        "BOOKS_API_HOST": "http://127.0.0.1:8000",
        "BOOKS_API_TOKEN": "secret-token-123"
      }
    }
  }
}
```

#### Option 2: Using `uv run` with `--directory`

```json
{
  "mcpServers": {
    "books-erp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/rajathkumar/localmcpchat", "python", "-m", "mcp_server.main"],
      "env": {
        "BOOKS_API_HOST": "http://127.0.0.1:8000",
        "BOOKS_API_TOKEN": "secret-token-123"
      }
    }
  }
}
```

### Configuration for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "books-erp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/rajathkumar/localmcpchat", "python", "-m", "mcp_server.main"],
      "env": {
        "BOOKS_API_HOST": "http://127.0.0.1:8000",
        "BOOKS_API_TOKEN": "secret-token-123"
      }
    }
  }
}
```

### Configuration for Cursor / Windsurf

Add to `.cursor/mcp.json` or `.windsurf/mcp.json`:

```json
{
  "mcpServers": {
    "books-erp": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/rajathkumar/localmcpchat", "python", "-m", "mcp_server.main"],
      "env": {
        "BOOKS_API_HOST": "http://127.0.0.1:8000",
        "BOOKS_API_TOKEN": "secret-token-123"
      }
    }
  }
}
```

## Usage Examples (Natural Language)

Once connected to an LLM via MCP, you can ask things like:

- "Add a new book called Dune by Frank Herbert, ISBN 9780441172719, published 1965-08-01, genre science, price $9.99, 25 copies in stock"
- "List all fantasy books"
- "Search for books by Tolkien"
- "Update the price of book ID 3 to $19.99"
- "Delete book ID 5"
- "Give me inventory statistics"
- "Show me all books that are out of stock"
- "Find books between $10 and $20"

## Architecture

```
mcp_server/
├── __init__.py          # Package init
├── main.py              # MCP server with 7 tools (FastMCP + httpx)
├── mcp_config.json      # Ready-to-use MCP server configuration
└── README.md            # This file
```

The MCP server calls the REST API over HTTP:

```
mcp_server/main.py  →  httpx  →  api/main.py (FastAPI)  →  api/store.py  →  SQLite
                                  ↑ Bearer token auth
```

This design ensures the MCP server and REST API share the same data layer, and all validation/auth rules are enforced by the API.

## Tech Stack

- **FastMCP** — MCP server framework (built on the `mcp` Python SDK)
- **httpx** — HTTP client for calling the REST API
- **stdio transport** — Standard MCP transport for local servers
- **Bearer token auth** — Authenticates with the REST API using `BOOKS_API_TOKEN`
