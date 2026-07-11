from api.tests.conftest import AUTH_HEADERS, SAMPLE_BOOK, SAMPLE_BOOK_2


class TestCreateBook:
    def test_create_book_success(self, client):
        resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert data["title"] == "The Hobbit"
        assert data["author"] == "J.R.R. Tolkien"
        assert data["genre"] == "fantasy"
        assert data["price"] == 15.99
        assert data["stock_quantity"] == 50
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_book_auto_increment_id(self, client):
        resp1 = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        resp2 = client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        assert resp1.json()["id"] == 1
        assert resp2.json()["id"] == 2

    def test_create_book_missing_required_field(self, client):
        book = {**SAMPLE_BOOK}
        del book["title"]
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_empty_title(self, client):
        book = {**SAMPLE_BOOK, "title": ""}
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_negative_price(self, client):
        book = {**SAMPLE_BOOK, "price": -5.0}
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_negative_stock(self, client):
        book = {**SAMPLE_BOOK, "stock_quantity": -1}
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_invalid_date_format(self, client):
        book = {**SAMPLE_BOOK, "published_date": "21-09-1937"}
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_invalid_genre(self, client):
        book = {**SAMPLE_BOOK, "genre": "cooking"}
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_create_book_default_genre(self, client):
        book = {**SAMPLE_BOOK}
        del book["genre"]
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 201
        assert resp.json()["genre"] == "other"

    def test_create_book_default_stock(self, client):
        book = {**SAMPLE_BOOK}
        del book["stock_quantity"]
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 201
        assert resp.json()["stock_quantity"] == 0

    def test_create_book_optional_description(self, client):
        book = {**SAMPLE_BOOK}
        del book["description"]
        resp = client.post("/books", json=book, headers=AUTH_HEADERS)
        assert resp.status_code == 201
        assert resp.json()["description"] is None
