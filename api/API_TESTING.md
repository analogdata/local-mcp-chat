# Books ERP API — Manual Testing Guide

This document provides ready-to-use `curl` commands and request bodies for manually testing every API endpoint.

## Prerequisites

Start the server:

```bash
export BOOKS_API_TOKEN="secret-token-123"
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

All examples assume the server is running at `http://127.0.0.1:8000`.

## Authentication

All `/books` endpoints require a Bearer token:

```
Authorization: Bearer secret-token-123
```

---

## 1. Root — `GET /`

**No auth required.**

```bash
curl -s http://127.0.0.1:8000/ | python3 -m json.tool
```

**Expected response (200):**

```json
{
    "service": "Books ERP API",
    "version": "1.0.0",
    "docs": "/docs"
}
```

---

## 2. Health — `GET /health`

**No auth required.**

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
```

**Expected response (200):**

```json
{
    "status": "healthy"
}
```

---

## 3. Create Book — `POST /books`

**Auth required.**

### Request Body

```json
{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0261102217",
    "published_date": "1937-09-21",
    "genre": "fantasy",
    "price": 15.99,
    "stock_quantity": 50,
    "description": "A fantasy novel about a hobbit"
}
```

### Field Reference

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `title` | string | Yes | 1–300 chars | — |
| `author` | string | Yes | 1–200 chars | — |
| `isbn` | string | Yes | 10–17 chars | — |
| `published_date` | string | Yes | Format: `YYYY-MM-DD` | — |
| `genre` | enum | No | See genre list below | `other` |
| `price` | float | Yes | > 0 | — |
| `stock_quantity` | int | No | >= 0 | `0` |
| `description` | string | No | max 2000 chars | `null` |

### Available Genres

`fiction`, `non_fiction`, `science`, `history`, `biography`, `fantasy`, `mystery`, `romance`, `thriller`, `children`, `other`

### curl

```bash
curl -s -X POST http://127.0.0.1:8000/books \
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
  }' | python3 -m json.tool
```

**Expected response (201):**

```json
{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0261102217",
    "published_date": "1937-09-21",
    "genre": "fantasy",
    "price": 15.99,
    "stock_quantity": 50,
    "description": "A fantasy novel about a hobbit",
    "id": 1,
    "created_at": "2026-07-11T12:38:59.220009Z",
    "updated_at": "2026-07-11T12:38:59.220012Z"
}
```

### Minimal request (only required fields)

```bash
curl -s -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "isbn": "978-0451524935",
    "published_date": "1949-06-08",
    "price": 12.50
  }' | python3 -m json.tool
```

**Expected response (201):** `genre` defaults to `"other"`, `stock_quantity` defaults to `0`, `description` defaults to `null`.

---

## 4. List Books — `GET /books`

**Auth required.**

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Records to skip (pagination offset) |
| `limit` | int | 20 | Max records (1–100) |
| `genre` | enum | — | Filter by genre |
| `author` | string | — | Partial, case-insensitive author match |
| `min_price` | float | — | Minimum price (inclusive) |
| `max_price` | float | — | Maximum price (inclusive) |
| `in_stock` | bool | false | Only books with stock > 0 |

### Examples

**List all books:**

```bash
curl -s http://127.0.0.1:8000/books \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**With pagination:**

```bash
curl -s "http://127.0.0.1:8000/books?skip=0&limit=5" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Filter by genre:**

```bash
curl -s "http://127.0.0.1:8000/books?genre=fantasy" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Filter by author (partial match):**

```bash
curl -s "http://127.0.0.1:8000/books?author=tolkien" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Filter by price range:**

```bash
curl -s "http://127.0.0.1:8000/books?min_price=10.0&max_price=20.0" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Only in-stock books:**

```bash
curl -s "http://127.0.0.1:8000/books?in_stock=true" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Combined filters:**

```bash
curl -s "http://127.0.0.1:8000/books?genre=fiction&min_price=10.0&max_price=15.0&in_stock=true&skip=0&limit=10" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Expected response (200):**

```json
[
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "978-0261102217",
        "published_date": "1937-09-21",
        "genre": "fantasy",
        "price": 15.99,
        "stock_quantity": 50,
        "description": "A fantasy novel about a hobbit",
        "id": 1,
        "created_at": "2026-07-11T12:38:59.220009Z",
        "updated_at": "2026-07-11T12:38:59.220012Z"
    }
]
```

---

## 5. Search Books — `GET /books/search`

**Auth required.**

Searches across title, author, and description (case-insensitive).

```bash
curl -s "http://127.0.0.1:8000/books/search?q=hobbit" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Search by author:**

```bash
curl -s "http://127.0.0.1:8000/books/search?q=orwell" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Search by description:**

```bash
curl -s "http://127.0.0.1:8000/books/search?q=fantasy+novel" \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Expected response (200):** Array of matching book objects (same format as list).

---

## 6. Get Book by ID — `GET /books/{id}`

**Auth required.**

```bash
curl -s http://127.0.0.1:8000/books/1 \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Expected response (200):** Single book object.

**Not found (404):**

```bash
curl -s http://127.0.0.1:8000/books/999 \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

```json
{
    "detail": "Book with ID 999 not found"
}
```

---

## 7. Update Book — `PUT /books/{id}`

**Auth required.** Partial update — only send fields you want to change.

### Request Body (all fields optional)

```json
{
    "title": "The Hobbit: Revised Edition",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0261102217",
    "published_date": "1937-09-21",
    "genre": "fantasy",
    "price": 18.99,
    "stock_quantity": 45,
    "description": "An updated description"
}
```

### Update single field:

```bash
curl -s -X PUT http://127.0.0.1:8000/books/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{"price": 18.99}' | python3 -m json.tool
```

### Update multiple fields:

```bash
curl -s -X PUT http://127.0.0.1:8000/books/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "price": 25.00,
    "stock_quantity": 100,
    "description": "Updated description text"
  }' | python3 -m json.tool
```

**Expected response (200):** Updated book object with new `updated_at` timestamp.

**Not found (404):**

```bash
curl -s -X PUT http://127.0.0.1:8000/books/999 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{"price": 18.99}' | python3 -m json.tool
```

```json
{
    "detail": "Book with ID 999 not found"
}
```

---

## 8. Delete Book — `DELETE /books/{id}`

**Auth required.**

```bash
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://127.0.0.1:8000/books/1 \
  -H "Authorization: Bearer secret-token-123"
```

**Expected response:** `204` (No Content)

**Not found (404):**

```bash
curl -s -X DELETE http://127.0.0.1:8000/books/999 \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

```json
{
    "detail": "Book with ID 999 not found"
}
```

---

## 9. Stats — `GET /books/stats`

**Auth required.**

```bash
curl -s http://127.0.0.1:8000/books/stats \
  -H "Authorization: Bearer secret-token-123" | python3 -m json.tool
```

**Expected response (200):**

```json
{
    "total_books": 2,
    "total_stock": 80,
    "total_value": 1229.55,
    "by_genre": {
        "fantasy": 1,
        "fiction": 1
    }
}
```

---

## 10. Authentication Errors

### Missing token (401):

```bash
curl -s http://127.0.0.1:8000/books | python3 -m json.tool
```

```json
{
    "detail": "Missing Authorization header"
}
```

### Wrong token (403):

```bash
curl -s http://127.0.0.1:8000/books \
  -H "Authorization: Bearer wrong-token" | python3 -m json.tool
```

```json
{
    "detail": "Invalid or expired token"
}
```

### Invalid scheme (401):

```bash
curl -s http://127.0.0.1:8000/books \
  -H "Authorization: Basic secret-token-123" | python3 -m json.tool
```

```json
{
    "detail": "Invalid authentication scheme. Use Bearer token."
}
```

---

## 11. Validation Errors (422)

### Missing required field:

```bash
curl -s -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{"author": "Test", "isbn": "1234567890", "published_date": "2020-01-01", "price": 10.0}' \
  | python3 -m json.tool
```

```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "title"],
            "msg": "Field required",
            "input": {...}
        }
    ]
}
```

### Invalid date format:

```bash
curl -s -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "title": "Test",
    "author": "Test",
    "isbn": "1234567890",
    "published_date": "01/01/2020",
    "price": 10.0
  }' | python3 -m json.tool
```

### Negative price:

```bash
curl -s -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "title": "Test",
    "author": "Test",
    "isbn": "1234567890",
    "published_date": "2020-01-01",
    "price": -5.0
  }' | python3 -m json.tool
```

### Invalid genre:

```bash
curl -s -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{
    "title": "Test",
    "author": "Test",
    "isbn": "1234567890",
    "published_date": "2020-01-01",
    "price": 10.0,
    "genre": "cooking"
  }' | python3 -m json.tool
```

---

## Quick Test Script

Run this to test the full CRUD lifecycle in order:

```bash
TOKEN="secret-token-123"
BASE="http://127.0.0.1:8000"
AUTH="Authorization: Bearer $TOKEN"

# Create
echo "=== CREATE ==="
BOOK=$(curl -s -X POST "$BASE/books" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"title":"The Hobbit","author":"J.R.R. Tolkien","isbn":"978-0261102217","published_date":"1937-09-21","genre":"fantasy","price":15.99,"stock_quantity":50,"description":"A fantasy novel"}')
echo "$BOOK" | python3 -m json.tool
ID=$(echo "$BOOK" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Read
echo "=== GET BY ID ==="
curl -s "$BASE/books/$ID" -H "$AUTH" | python3 -m json.tool

# List
echo "=== LIST ==="
curl -s "$BASE/books" -H "$AUTH" | python3 -m json.tool

# Search
echo "=== SEARCH ==="
curl -s "$BASE/books/search?q=hobbit" -H "$AUTH" | python3 -m json.tool

# Update
echo "=== UPDATE ==="
curl -s -X PUT "$BASE/books/$ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"price":18.99,"stock_quantity":45}' | python3 -m json.tool

# Stats
echo "=== STATS ==="
curl -s "$BASE/books/stats" -H "$AUTH" | python3 -m json.tool

# Delete
echo "=== DELETE ==="
curl -s -o /dev/null -w "HTTP %{http_code}" -X DELETE "$BASE/books/$ID" -H "$AUTH"
echo ""

# Verify deleted
echo "=== VERIFY DELETED ==="
curl -s "$BASE/books/$ID" -H "$AUTH" | python3 -m json.tool
```
