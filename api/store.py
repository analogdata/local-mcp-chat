import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .models import Book, BookCreate, BookUpdate

DEFAULT_DB_PATH = os.environ.get("BOOKS_DB_PATH", "books.db")


class BookStore:
    """SQLite-backed store for books with auto-incrementing IDs."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT NOT NULL,
                published_date TEXT NOT NULL,
                genre TEXT NOT NULL DEFAULT 'other',
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def _row_to_book(self, row: sqlite3.Row) -> Book:
        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            isbn=row["isbn"],
            published_date=row["published_date"],
            genre=row["genre"],
            price=row["price"],
            stock_quantity=row["stock_quantity"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create(self, data: BookCreate) -> Book:
        now = datetime.now(timezone.utc).isoformat()
        cursor = self._conn.execute(
            """
            INSERT INTO books (title, author, isbn, published_date, genre, price, stock_quantity, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.title,
                data.author,
                data.isbn,
                data.published_date,
                data.genre.value,
                data.price,
                data.stock_quantity,
                data.description,
                now,
                now,
            ),
        )
        self._conn.commit()
        return self.get(cursor.lastrowid)

    def get(self, book_id: int) -> Optional[Book]:
        row = self._conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        return self._row_to_book(row) if row else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        genre: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
    ) -> list[Book]:
        query = "SELECT * FROM books WHERE 1=1"
        params: list = []
        if genre:
            query += " AND genre = ?"
            params.append(genre)
        if author:
            query += " AND LOWER(author) LIKE ?"
            params.append(f"%{author.lower()}%")
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        if in_stock_only:
            query += " AND stock_quantity > 0"
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_book(r) for r in rows]

    def count(
        self,
        genre: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
    ) -> int:
        query = "SELECT COUNT(*) as c FROM books WHERE 1=1"
        params: list = []
        if genre:
            query += " AND genre = ?"
            params.append(genre)
        if author:
            query += " AND LOWER(author) LIKE ?"
            params.append(f"%{author.lower()}%")
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        if in_stock_only:
            query += " AND stock_quantity > 0"
        row = self._conn.execute(query, params).fetchone()
        return row["c"]

    def search(self, query: str) -> list[Book]:
        pattern = f"%{query.lower()}%"
        rows = self._conn.execute(
            """
            SELECT * FROM books
            WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(COALESCE(description, '')) LIKE ?
            ORDER BY id
            """,
            (pattern, pattern, pattern),
        ).fetchall()
        return [self._row_to_book(r) for r in rows]

    def update(self, book_id: int, data: BookUpdate) -> Optional[Book]:
        book = self.get(book_id)
        if book is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return book
        if "genre" in update_data and update_data["genre"] is not None:
            update_data["genre"] = update_data["genre"].value
        now = datetime.now(timezone.utc).isoformat()
        set_clauses = ", ".join(f"{k} = ?" for k in update_data)
        set_clauses += ", updated_at = ?"
        params = list(update_data.values()) + [now, book_id]
        self._conn.execute(f"UPDATE books SET {set_clauses} WHERE id = ?", params)
        self._conn.commit()
        return self.get(book_id)

    def delete(self, book_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def stats(self) -> dict:
        total_row = self._conn.execute(
            "SELECT COUNT(*) as c, COALESCE(SUM(stock_quantity), 0) as s, COALESCE(SUM(price * stock_quantity), 0) as v FROM books"
        ).fetchone()
        genre_rows = self._conn.execute(
            "SELECT genre, COUNT(*) as count FROM books GROUP BY genre"
        ).fetchall()
        by_genre = {row["genre"]: row["count"] for row in genre_rows}
        return {
            "total_books": total_row["c"],
            "total_stock": total_row["s"],
            "total_value": round(total_row["v"], 2),
            "by_genre": by_genre,
        }

    def close(self) -> None:
        self._conn.close()


store = BookStore()
