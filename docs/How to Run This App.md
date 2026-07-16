# How to Run This App

This guide runs the Local AI Books ERP from start to finish:

1. Start the FastAPI Books ERP service.
2. Confirm that the API and SQLite database are available.
3. Configure LM Studio to start the MCP server.
4. Select a model that supports tool calling.
5. Ask the model to manage the book inventory.

The system uses two processes. **FastAPI owns the API and SQLite database. LM Studio starts the MCP server and the local LLM.**

```text
Terminal                                    LM Studio
────────                                    ─────────
FastAPI / Uvicorn                           Local LLM
http://127.0.0.1:8000                        │
SQLite: books.db                             │ stdio / MCP
       ▲                                     ▼
       └──── authenticated HTTP ────── FastMCP server
```

---

## Prerequisites

Install the following before starting:

- Python `3.13` or later.
- [uv](https://docs.astral.sh/uv/) package manager.
- [LM Studio](https://lmstudio.ai/).
- A local instruct model with explicit tool/function-calling support. A larger reasoning-capable model is more reliable than sub-1B models for MCP tool calls.

> The project uses Python's built-in `sqlite3`; no external database server is required.

---

## 1. Open a Terminal at the Project Root

Open a terminal in the folder that contains `pyproject.toml`, `api/`, and `mcp_server/`.

```bash
cd /Users/rajathkumar/localmcpchat
```

Install the locked project dependencies:

```bash
uv sync
```

This installs FastAPI, FastMCP, Uvicorn, pytest, and the required HTTP client dependencies into the project environment.

---

## 2. Configure the API Token

The Books ERP API protects all `/books` routes with a Bearer token. Set the token before starting the API:

```bash
export BOOKS_API_TOKEN="secret-token-123"
```

`secret-token-123` is the local development default. You can use a different value, but the exact same value must be configured as `BOOKS_API_TOKEN` in LM Studio's MCP configuration.

```text
MCP Server                          FastAPI
BOOKS_API_TOKEN = <value>  ──────►  verifies the same <value>
```

---

## 3. Start the FastAPI Service

Start the API in the first terminal:

```bash
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

The `--reload` option is useful during development because Uvicorn restarts the API after Python source changes.

You should see output similar to the following: Uvicorn is listening on port `8000` and the application startup has completed.

![Terminal showing FastAPI and Uvicorn started](images/localmcpchathow1.png)

### Verify the Health Endpoint

Keep the API terminal running. Open a second terminal and run:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

You can also open these URLs in a browser:

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/docs` | Interactive Swagger UI for the REST API |
| `http://127.0.0.1:8000/redoc` | ReDoc API reference |
| `http://127.0.0.1:8000/health` | Lightweight service health check |

At this point, `books.db` is created in the project root if it does not already exist. It stores all inventory data between API restarts.

---

## 4. Understand the MCP Server's Role

The MCP server is a bridge between LM Studio and the REST API. It does **not** access SQLite directly. Each tool call becomes an authenticated HTTP request to FastAPI.

```text
LM Studio tool call
      │
      ▼
FastMCP tool function
      │  Authorization: Bearer <BOOKS_API_TOKEN>
      ▼
FastAPI endpoint
      │  Pydantic validation + BookStore
      ▼
SQLite books.db
```

For reference, the MCP server can be started manually with:

```bash
export BOOKS_API_HOST="http://127.0.0.1:8000"
export BOOKS_API_TOKEN="secret-token-123"
uv run python -m mcp_server.main
```

It uses **stdio transport**, so it waits for an MCP client on standard input; it does not open a browser page or an HTTP port. In normal use, do not start it manually. LM Studio launches it from the MCP configuration in the next step.

![Terminal showing the FastMCP server started with stdio transport](images/localmcpchathow2.png)

---

## 5. Configure the MCP Server in LM Studio

Open LM Studio, then open its MCP server configuration. Copy the contents of `mcp_server/mcp_config.json` into the configuration editor:

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

The settings have distinct responsibilities:

| Setting | Meaning |
|---|---|
| `command` and `args` | Starts FastMCP through the project's `uv` environment |
| `cwd` | Lets Python resolve the `mcp_server` package from this repository |
| `BOOKS_API_HOST` | Points the MCP server to the running FastAPI process |
| `BOOKS_API_TOKEN` | Must match the token used by FastAPI |

Save the configuration. LM Studio reloads the configured MCP server and discovers its tools.

![LM Studio MCP configuration with API host and token](images/localmcpchathow3.png)

### Confirm Tool Discovery

After the configuration is saved, enable the `books-erp` integration in the chat interface. LM Studio should display the Books ERP tools, including:

- `create_book`
- `list_books`
- `get_book`
- `search_books`
- `get_book_stats`
- `update_book`
- `delete_book`
- Intent-friendly aliases such as `get_books`, `get_all_books`, `add_book`, and `find_books`

If the tools are not visible, check that the FastAPI health URL succeeds, the configured working directory is correct, and the host/token values match.

---

## 6. Choose a Tool-Calling Model

Tool discovery and tool execution are different abilities. A model can see an MCP tool but still fail to produce the structured call required to invoke it.

Choose an instruct model that is documented to support tool/function calling. In practice, larger reasoning-capable local models are more reliable for this workflow than tiny models.

```text
User request
   │
   ▼
Model identifies inventory intent
   │
   ▼
Model selects tool + serializes valid arguments
   │
   ▼
LM Studio calls MCP server
   │
   ▼
Model receives actual API result and writes the answer
```

In LM Studio, select the model from the loaded-model picker before opening or continuing the Books ERP chat.

![LM Studio model picker showing available local models](images/localmcpchathow4.png)

> If a model prints JSON Schema fragments such as `{"type":"object"}` instead of calling a tool, the API and MCP server are not necessarily broken. That behavior indicates that the selected model or tool-call parser cannot reliably generate valid structured tool calls. Try a model with stronger function-calling support.

---

## 7. Open a Chat and Enable the Books ERP Integration

Create or open a chat in LM Studio. Confirm that the `books-erp` integration is enabled and its tools are selected for the chat.

![LM Studio chat with the Books ERP integration and discovered tools enabled](images/localmcpchathow5.png)

Try one of these prompts:

```text
List all the books.
```

```text
Show all fantasy books that are in stock.
```

```text
Search for books by Tolkien.
```

```text
Give me the current inventory statistics.
```

To add a book, supply the required fields clearly:

```text
Add Dune by Frank Herbert. ISBN: 9780441172719. Published: 1965-08-01.
Genre: science. Price: 9.99. Stock quantity: 25.
```

The canonical `list_books` tool supports filters and pagination. The zero-argument `get_books` and `get_all_books` aliases are intentionally available for straightforward “show all books” requests.

---

## 8. Verify the Grounded Result

When tool calling succeeds, LM Studio shows the selected tool, waits for the MCP result, and then writes an answer from the book objects returned by the API.

![LM Studio displaying a get_books tool call and the returned inventory](images/localmcpchathow6.png)

The full execution path is:

```text
1. User asks for inventory data in LM Studio.
2. The model selects a Books ERP MCP tool.
3. FastMCP converts that call into an authenticated HTTP request.
4. FastAPI verifies the Bearer token and validates the request.
5. BookStore runs parameterized SQLite operations.
6. FastAPI returns JSON to the MCP server.
7. LM Studio passes the actual result to the model for its final response.
```

The response is grounded in `books.db`; the model should describe the data returned by the tool rather than inventing inventory entries.

---

## 9. Test the REST API Without LM Studio

Testing the REST API separately narrows down configuration issues. Use the same Bearer token configured above.

### List books

```bash
curl http://127.0.0.1:8000/books \
  -H "Authorization: Bearer secret-token-123"
```

### Create a book

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0261102217",
    "published_date": "1937-09-21",
    "genre": "fantasy",
    "price": 15.99,
    "stock_quantity": 50,
    "description": "A fantasy novel about a hobbit"
  }'
```

### Run the automated test suite

```bash
uv run pytest -v
```

The test suite uses an in-memory SQLite database and does not modify your local `books.db` inventory.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| LM Studio shows no `books-erp` tools | MCP process did not start or configuration was not saved | Verify `cwd`, `command`, `args`, then save/reload the MCP config |
| Tools are visible but return connection errors | FastAPI is not running or `BOOKS_API_HOST` is wrong | Run the health check and use `http://127.0.0.1:8000` |
| Tool call returns `401` or `403` | Token is missing or differs between processes | Set the same `BOOKS_API_TOKEN` in the API terminal and MCP config |
| Model prints JSON schema instead of calling a tool | Model/parser lacks reliable tool-calling behavior | Choose a stronger tool-calling model and start a new chat |
| API returns `422` | Required data is absent or a field fails validation | Check title, author, ISBN, date, genre, price, and stock values |
| A book is not present after restart | API used a different database path | Check `BOOKS_DB_PATH` and the API process working directory |

---

## Stop the App

- Stop FastAPI with `Ctrl+C` in the terminal running Uvicorn.
- LM Studio stops the MCP server when the integration or application is stopped.
- Do not delete `books.db` unless you intentionally want to remove local inventory data.

---

## Next Steps

- Use `http://127.0.0.1:8000/docs` to explore all REST endpoints manually.
- Review [the API testing guide](../api/API_TESTING.md) for complete request bodies and responses.
- Review [the MCP server guide](../mcp_server/README.md) for tool and client configuration details.
- Read [the architecture blog post](../BLOG.md) for the design rationale behind the system.
