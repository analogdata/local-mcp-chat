from api.tests.conftest import AUTH_HEADERS, SAMPLE_BOOK


class TestUpdateBook:
    def test_update_book_partial(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.put(f"/books/{book_id}", json={"price": 19.99}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == 19.99
        assert data["title"] == "The Hobbit"

    def test_update_book_multiple_fields(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.put(
            f"/books/{book_id}",
            json={"price": 25.00, "stock_quantity": 100, "description": "Updated desc"},
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == 25.00
        assert data["stock_quantity"] == 100
        assert data["description"] == "Updated desc"

    def test_update_book_updated_at_changes(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        original_updated = create_resp.json()["updated_at"]
        resp = client.put(f"/books/{book_id}", json={"price": 19.99}, headers=AUTH_HEADERS)
        assert resp.json()["updated_at"] != original_updated

    def test_update_book_not_found(self, client):
        resp = client.put("/books/999", json={"price": 19.99}, headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_update_book_invalid_price(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.put(f"/books/{book_id}", json={"price": -10.0}, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_update_book_invalid_date(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.put(f"/books/{book_id}", json={"published_date": "01/01/2000"}, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_update_book_empty_body(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.put(f"/books/{book_id}", json={}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["title"] == "The Hobbit"


class TestDeleteBook:
    def test_delete_book_success(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        resp = client.delete(f"/books/{book_id}", headers=AUTH_HEADERS)
        assert resp.status_code == 204

    def test_delete_book_not_found(self, client):
        resp = client.delete("/books/999", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_delete_book_already_deleted(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        client.delete(f"/books/{book_id}", headers=AUTH_HEADERS)
        resp = client.delete(f"/books/{book_id}", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_delete_then_get_returns_404(self, client):
        create_resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        book_id = create_resp.json()["id"]
        client.delete(f"/books/{book_id}", headers=AUTH_HEADERS)
        resp = client.get(f"/books/{book_id}", headers=AUTH_HEADERS)
        assert resp.status_code == 404
