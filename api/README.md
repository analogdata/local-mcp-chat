# Books ERP API

A complete CRUD API for managing a book inventory system, built with **FastAPI** and **Pydantic**.

## Features

- **Create** books with validated fields (title, author, ISBN, genre, price, stock, etc.)
- **Read** all books with pagination, filtering (genre, author, price range, in-stock)
- **Read** a single book by ID
- **Search** books by title, author, or description
- **Update** books with partial updates (only sent fields are changed)
- **Delete** books from the inventory
- **Stats** endpoint with aggregate inventory metrics
- **Bearer token authentication** on all book endpoints
- **Auto-generated interactive docs** at `/docs` (Swagger UI) and `/redoc`

## Project Structure

```
api/
├── __init__.py          # Package init
├── main.py              # FastAPI app with all route handlers
├── models.py            # Pydantic models (BookBase, BookCreate, BookUpdate, etc.)
├── store.py             # In-memory BookStore with CRUD + search + stats
├── auth.py              # Bearer token authentication dependency
├── README.md            # This file
├── API_TESTING.md       # Manual testing guide with request/response examples
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures (client, auth headers, sample data)
    ├── test_health.py       # Root and health endpoint tests
    ├── test_auth.py         # Authentication and authorization tests
    ├── test_create.py       # Book creation validation tests
    ├── test_read.py         # List, get, search, and stats tests
    ├── test_update_delete.py # Update and delete operation tests
    └── test_store.py        # Direct BookStore unit tests
```

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# From the project root
uv sync
```

### Running the Server

```bash
# Set the Bearer token (defaults to "secret-token-123" if not set)
export BOOKS_API_TOKEN="your-secret-token"

# Start the server
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000`.

- **Interactive docs (Swagger UI):** `http://127.0.0.1:8000/docs`
- **ReDoc docs:** `http://127.0.0.1:8000/redoc`

## Authentication

All `/books` endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

The token is configured via the `BOOKS_API_TOKEN` environment variable (defaults to `secret-token-123`).

The `/` (root) and `/health` endpoints are public and do not require authentication.

### Auth Responses

| Status | Meaning |
|--------|---------|
| `401 Unauthorized` | Missing `Authorization` header or invalid scheme |
| `403 Forbidden` | Token is incorrect |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | Service info |
| `GET` | `/health` | No | Health check |
| `POST` | `/books` | Yes | Create a new book |
| `GET` | `/books` | Yes | List books (with filters & pagination) |
| `GET` | `/books/search?q=` | Yes | Search books by title/author/description |
| `GET` | `/books/stats` | Yes | Aggregate inventory statistics |
| `GET` | `/books/{id}` | Yes | Get a single book by ID |
| `PUT` | `/books/{id}` | Yes | Update a book (partial update) |
| `DELETE` | `/books/{id}` | Yes | Delete a book |

### Query Parameters for `GET /books`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip (pagination) |
| `limit` | int | 20 | Max records to return (1–100) |
| `genre` | enum | None | Filter by genre |
| `author` | string | None | Filter by author (partial, case-insensitive) |
| `min_price` | float | None | Minimum price filter |
| `max_price` | float | None | Maximum price filter |
| `in_stock` | bool | false | Only show books with stock > 0 |

### Available Genres

`fiction`, `non_fiction`, `science`, `history`, `biography`, `fantasy`, `mystery`, `romance`, `thriller`, `children`, `other`

## Running Tests

```bash
# Run all tests
uv run pytest -v

# Run a specific test file
uv run pytest api/tests/test_auth.py -v

# Run with coverage report
uv run pytest --tb=short
```

**64 tests** covering:
- Health and root endpoints
- Authentication (missing token, wrong token, invalid scheme)
- Book creation with validation (required fields, price, stock, date format, genre)
- Listing with pagination and all filter combinations
- Single book retrieval (found and not found)
- Search by title, author, description
- Stats endpoint
- Partial updates (single field, multiple fields, updated_at changes)
- Delete (success, not found, already deleted, cascade verification)
- Direct BookStore unit tests

## Tech Stack

- **FastAPI** — Web framework
- **Pydantic** — Data validation and serialization
- **Uvicorn** — ASGI server
- **pytest** — Testing framework
- **httpx** — HTTP client for testing
