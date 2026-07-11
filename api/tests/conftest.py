import os

import pytest
from fastapi.testclient import TestClient

# Set a known token and in-memory DB before importing the app
os.environ["BOOKS_API_TOKEN"] = "test-token-abc"
os.environ["BOOKS_DB_PATH"] = ":memory:"

from api.main import app
from api.store import store


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    store._conn.execute("DELETE FROM books")
    store._conn.execute("DELETE FROM sqlite_sequence WHERE name='books'")
    store._conn.commit()
    yield
    store._conn.execute("DELETE FROM books")
    store._conn.execute("DELETE FROM sqlite_sequence WHERE name='books'")
    store._conn.commit()


VALID_TOKEN = "test-token-abc"
AUTH_HEADERS = {"Authorization": f"Bearer {VALID_TOKEN}"}

SAMPLE_BOOK = {
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0261102217",
    "published_date": "1937-09-21",
    "genre": "fantasy",
    "price": 15.99,
    "stock_quantity": 50,
    "description": "A fantasy novel about a hobbit",
}

SAMPLE_BOOK_2 = {
    "title": "1984",
    "author": "George Orwell",
    "isbn": "978-0451524935",
    "published_date": "1949-06-08",
    "genre": "fiction",
    "price": 12.50,
    "stock_quantity": 30,
}
