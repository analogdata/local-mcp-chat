from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from .auth import verify_token
from .models import BookCreate, BookResponse, BookStats, BookUpdate, Genre
from .store import store

app = FastAPI(
    title="Books ERP API",
    description="A complete CRUD API for managing a book inventory system.",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Root / Health
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "Books ERP API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ──────────────────────────────────────────────
# CREATE — POST /books
# ──────────────────────────────────────────────

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book: BookCreate, _: None = Depends(verify_token)):
    """Add a new book to the inventory."""
    return store.create(book)


# ──────────────────────────────────────────────
# READ — GET /books  (list with filters + pagination)
# ──────────────────────────────────────────────

@app.get("/books", response_model=list[BookResponse], tags=["Books"])
def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    genre: Optional[Genre] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author (partial match)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: bool = Query(False, description="Only show books with stock > 0"),
    _: None = Depends(verify_token),
):
    """List books with optional filtering and pagination."""
    return store.get_all(
        skip=skip,
        limit=limit,
        genre=genre.value if genre else None,
        author=author,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock,
    )


# ──────────────────────────────────────────────
# SEARCH — GET /books/search?q=...
# (must be before /books/{book_id} to avoid path conflict)
# ──────────────────────────────────────────────

@app.get("/books/search", response_model=list[BookResponse], tags=["Books"])
def search_books(
    q: str = Query(..., min_length=1, description="Search query for title, author, or description"),
    _: None = Depends(verify_token),
):
    """Search books by title, author, or description."""
    return store.search(q)


# ──────────────────────────────────────────────
# STATS — GET /books/stats
# (must be before /books/{book_id} to avoid path conflict)
# ──────────────────────────────────────────────

@app.get("/books/stats", response_model=BookStats, tags=["Books"])
def book_stats(_: None = Depends(verify_token)):
    """Get aggregate statistics about the book inventory."""
    return store.stats()


# ──────────────────────────────────────────────
# READ — GET /books/{book_id}
# ──────────────────────────────────────────────

@app.get("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def get_book(book_id: int, _: None = Depends(verify_token)):
    """Retrieve a single book by its ID."""
    book = store.get(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found")
    return book


# ──────────────────────────────────────────────
# UPDATE — PUT /books/{book_id}
# ──────────────────────────────────────────────

@app.put("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def update_book(book_id: int, book_update: BookUpdate, _: None = Depends(verify_token)):
    """Update an existing book. Only provided fields are changed (partial update)."""
    book = store.update(book_id, book_update)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found")
    return book


# ──────────────────────────────────────────────
# DELETE — DELETE /books/{book_id}
# ──────────────────────────────────────────────

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int, _: None = Depends(verify_token)):
    """Remove a book from the inventory."""
    if not store.delete(book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {book_id} not found")
    return None

