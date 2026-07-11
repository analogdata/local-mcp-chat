"""Books ERP MCP Server.

Exposes all Books ERP CRUD operations as MCP tools so that LLM clients
like LM Studio (with Qwen, Gemma3, etc.) can manage the book inventory
through natural language.

This server communicates with the Books ERP REST API over HTTP using
the configured API host address and Bearer token.
"""

import os

import httpx
from fastmcp import FastMCP

API_HOST = os.environ.get("BOOKS_API_HOST", "http://127.0.0.1:8000")
API_TOKEN = os.environ.get("BOOKS_API_TOKEN", "secret-token-123")

HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def _api_get(path: str, params: dict | None = None) -> dict | list:
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(f"{API_HOST}{path}", headers=HEADERS, params=params)
        resp.raise_for_status()
        return resp.json()


def _api_post(path: str, json_body: dict) -> dict:
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(f"{API_HOST}{path}", headers=HEADERS, json=json_body)
        resp.raise_for_status()
        return resp.json()


def _api_put(path: str, json_body: dict) -> dict:
    with httpx.Client(timeout=10.0) as client:
        resp = client.put(f"{API_HOST}{path}", headers=HEADERS, json=json_body)
        resp.raise_for_status()
        return resp.json()


def _api_delete(path: str) -> int:
    with httpx.Client(timeout=10.0) as client:
        resp = client.delete(f"{API_HOST}{path}", headers=HEADERS)
        resp.raise_for_status()
        return resp.status_code


mcp = FastMCP(
    name="Books ERP MCP Server",
    instructions=(
        "You are a book inventory assistant. Use these tools to manage books:\n"
        "\n"
        "AVAILABLE TOOLS (use these exact names):\n"
        "  - create_book: Add a new book (also: add_book)\n"
        "  - list_books: List all books with optional filters (also: get_books, get_all_books)\n"
        "  - get_book: Get a single book by its ID (also: get_book_by_id)\n"
        "  - search_books: Search books by title, author, or description (also: find_books)\n"
        "  - get_book_stats: Get inventory statistics (also: book_stats, get_stats)\n"
        "  - update_book: Update an existing book (also: edit_book)\n"
        "  - delete_book: Delete a book (also: remove_book)\n"
        "\n"
        "When the user asks to 'list books' or 'show books', use list_books.\n"
        "When the user asks to 'add a book', use create_book.\n"
        f"API endpoint: {API_HOST}"
    ),
)


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

@mcp.tool
def create_book(
    title: str,
    author: str,
    isbn: str,
    published_date: str,
    price: float,
    genre: str = "other",
    stock_quantity: int = 0,
    description: str | None = None,
) -> dict:
    """Add a new book to the inventory.

    Args:
        title: Title of the book (1-300 chars)
        author: Author name (1-200 chars)
        isbn: ISBN identifier (10-17 chars)
        published_date: Publication date in YYYY-MM-DD format
        price: Price of the book (must be > 0)
        genre: One of: fiction, non_fiction, science, history, biography, fantasy, mystery, romance, thriller, children, other
        stock_quantity: Number of copies in stock (>= 0, default 0)
        description: Optional description (max 2000 chars)

    Returns:
        The created book object with id, created_at, and updated_at.
    """
    body: dict = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "published_date": published_date,
        "price": price,
        "genre": genre,
        "stock_quantity": stock_quantity,
    }
    if description is not None:
        body["description"] = description
    return _api_post("/books", body)


# ──────────────────────────────────────────────
# READ — List with filters
# ──────────────────────────────────────────────

@mcp.tool
def list_books(
    skip: int = 0,
    limit: int = 20,
    genre: str | None = None,
    author: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool = False,
) -> list[dict]:
    """List all books. Can be called with no arguments to get all books. All parameters are optional filters.

    Args:
        skip: Number of records to skip (default 0)
        limit: Max records to return (default 20)
        genre: Filter by genre
        author: Filter by author name
        min_price: Minimum price filter
        max_price: Maximum price filter
        in_stock: If true, only show books with stock > 0

    Returns:
        List of book objects.
    """
    params: dict = {"skip": skip, "limit": limit}
    if genre:
        params["genre"] = genre
    if author:
        params["author"] = author
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if in_stock:
        params["in_stock"] = "true"
    return _api_get("/books", params=params)


# ──────────────────────────────────────────────
# READ — Get by ID
# ──────────────────────────────────────────────

@mcp.tool
def get_book(book_id: int) -> dict | str:
    """Retrieve a single book by its ID.

    Args:
        book_id: The unique ID of the book

    Returns:
        The book object if found, or an error message if not found.
    """
    try:
        return _api_get(f"/books/{book_id}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Book with ID {book_id} not found."
        raise


# ──────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────

@mcp.tool
def search_books(query: str) -> list[dict]:
    """Search books by title, author, or description (case-insensitive).

    Args:
        query: Search term to look for in title, author, or description

    Returns:
        List of matching book objects.
    """
    return _api_get("/books/search", params={"q": query})


# ──────────────────────────────────────────────
# STATS
# ──────────────────────────────────────────────

@mcp.tool
def get_book_stats() -> dict:
    """Get aggregate statistics about the book inventory.

    Returns:
        Dictionary with total_books, total_stock, total_value, and by_genre breakdown.
    """
    return _api_get("/books/stats")


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

@mcp.tool
def update_book(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    published_date: str | None = None,
    genre: str | None = None,
    price: float | None = None,
    stock_quantity: int | None = None,
    description: str | None = None,
) -> dict | str:
    """Update an existing book. Only provided fields are changed (partial update).

    Args:
        book_id: The ID of the book to update
        title: New title (optional)
        author: New author (optional)
        isbn: New ISBN (optional)
        published_date: New publication date in YYYY-MM-DD format (optional)
        genre: New genre (optional)
        price: New price, must be > 0 (optional)
        stock_quantity: New stock quantity, must be >= 0 (optional)
        description: New description (optional)

    Returns:
        The updated book object, or an error message if the book was not found.
    """
    body: dict = {}
    if title is not None:
        body["title"] = title
    if author is not None:
        body["author"] = author
    if isbn is not None:
        body["isbn"] = isbn
    if published_date is not None:
        body["published_date"] = published_date
    if genre is not None:
        body["genre"] = genre
    if price is not None:
        body["price"] = price
    if stock_quantity is not None:
        body["stock_quantity"] = stock_quantity
    if description is not None:
        body["description"] = description
    try:
        return _api_put(f"/books/{book_id}", body)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Book with ID {book_id} not found."
        raise


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

@mcp.tool
def delete_book(book_id: int) -> str:
    """Delete a book from the inventory.

    Args:
        book_id: The ID of the book to delete

    Returns:
        Success or error message.
    """
    try:
        _api_delete(f"/books/{book_id}")
        return f"Book with ID {book_id} has been deleted."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Book with ID {book_id} not found."
        raise


# ──────────────────────────────────────────────
# ALIASES — Common alternative names that small
# models (Qwen 1B, Gemma3 1B) naturally generate
# ──────────────────────────────────────────────

@mcp.tool
def get_books() -> list[dict]:
    """Get all books from the inventory. Call this when the user wants to list or show all books. No arguments needed.

    Returns:
        List of all book objects in the inventory.
    """
    return _api_get("/books")


@mcp.tool
def get_all_books() -> list[dict]:
    """Get all books from the inventory. Same as get_books. No arguments needed.

    Returns:
        List of all book objects.
    """
    return _api_get("/books")


@mcp.tool
def add_book(
    title: str,
    author: str,
    isbn: str,
    published_date: str,
    price: float,
    genre: str = "other",
    stock_quantity: int = 0,
    description: str | None = None,
) -> dict:
    """Add a new book to the inventory. Same as create_book.

    Args:
        title: Title of the book
        author: Author name
        isbn: ISBN identifier (10-17 chars)
        published_date: Publication date in YYYY-MM-DD format
        price: Price of the book (must be > 0)
        genre: One of: fiction, non_fiction, science, history, biography, fantasy, mystery, romance, thriller, children, other
        stock_quantity: Number of copies in stock (>= 0, default 0)
        description: Optional description

    Returns:
        The created book object with id, created_at, and updated_at.
    """
    body: dict = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "published_date": published_date,
        "price": price,
        "genre": genre,
        "stock_quantity": stock_quantity,
    }
    if description is not None:
        body["description"] = description
    return _api_post("/books", body)


@mcp.tool
def remove_book(book_id: int) -> str:
    """Remove/delete a book from the inventory. Same as delete_book.

    Args:
        book_id: The ID of the book to delete

    Returns:
        Success or error message.
    """
    try:
        _api_delete(f"/books/{book_id}")
        return f"Book with ID {book_id} has been deleted."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Book with ID {book_id} not found."
        raise


@mcp.tool
def find_books(query: str) -> list[dict]:
    """Find/search books by title, author, or description. Same as search_books.

    Args:
        query: Search term to look for

    Returns:
        List of matching book objects.
    """
    return _api_get("/books/search", params={"q": query})


@mcp.tool
def get_stats() -> dict:
    """Get inventory statistics. Same as get_book_stats.

    Returns:
        Dictionary with total_books, total_stock, total_value, and by_genre.
    """
    return _api_get("/books/stats")


if __name__ == "__main__":
    mcp.run(transport="stdio")
