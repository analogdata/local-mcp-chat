from api.tests.conftest import AUTH_HEADERS, SAMPLE_BOOK, SAMPLE_BOOK_2


class TestListBooks:
    def test_list_empty(self, client):
        resp = client.get("/books", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_all(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_pagination_skip(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?skip=1", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "1984"

    def test_list_pagination_limit(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?limit=1", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1

    def test_list_filter_by_genre(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?genre=fantasy", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["genre"] == "fantasy"

    def test_list_filter_by_author(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?author=orwell", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert "Orwell" in resp.json()[0]["author"]

    def test_list_filter_by_min_price(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?min_price=14.0", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["price"] >= 14.0

    def test_list_filter_by_max_price(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?max_price=14.0", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["price"] <= 14.0

    def test_list_filter_in_stock(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json={**SAMPLE_BOOK_2, "stock_quantity": 0}, headers=AUTH_HEADERS)
        resp = client.get("/books?in_stock=true", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["stock_quantity"] > 0

    def test_list_combined_filters(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books?genre=fiction&min_price=10.0&max_price=15.0", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "1984"


class TestGetBook:
    def test_get_book_by_id(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.get(f"/books/{book_id}", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["title"] == "The Hobbit"

    def test_get_book_not_found(self, client):
        resp = client.get("/books/999", headers=AUTH_HEADERS)
        assert resp.status_code == 404
        assert "999" in resp.json()["detail"]


class TestSearchBooks:
    def test_search_by_title(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books/search?q=hobbit", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "The Hobbit"

    def test_search_by_author(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books/search?q=orwell", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1
        assert "Orwell" in resp.json()[0]["author"]

    def test_search_by_description(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        resp = client.get("/books/search?q=fantasy+novel", headers=AUTH_HEADERS)
        assert len(resp.json()) == 1

    def test_search_no_results(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        resp = client.get("/books/search?q=nonexistentbook", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_search_empty_query_rejected(self, client):
        resp = client.get("/books/search?q=", headers=AUTH_HEADERS)
        assert resp.status_code == 422


class TestStats:
    def test_stats_empty(self, client):
        resp = client.get("/books/stats", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_books"] == 0
        assert data["total_stock"] == 0
        assert data["total_value"] == 0.0
        assert data["by_genre"] == {}

    def test_stats_with_books(self, client):
        client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        client.post("/books", json=SAMPLE_BOOK_2, headers=AUTH_HEADERS)
        resp = client.get("/books/stats", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_books"] == 2
        assert data["total_stock"] == 80
        assert data["total_value"] == round(15.99 * 50 + 12.50 * 30, 2)
        assert data["by_genre"] == {"fantasy": 1, "fiction": 1}
