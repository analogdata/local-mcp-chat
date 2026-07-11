from api.tests.conftest import AUTH_HEADERS, SAMPLE_BOOK, VALID_TOKEN


class TestAuth:
    def test_create_without_token(self, client):
        resp = client.post("/books", json=SAMPLE_BOOK)
        assert resp.status_code == 401

    def test_create_with_wrong_token(self, client):
        resp = client.post("/books", json=SAMPLE_BOOK, headers={"Authorization": "Bearer wrong-token"})
        assert resp.status_code == 403

    def test_create_with_invalid_scheme(self, client):
        resp = client.post("/books", json=SAMPLE_BOOK, headers={"Authorization": "Basic test-token-abc"})
        assert resp.status_code == 401

    def test_list_without_token(self, client):
        resp = client.get("/books")
        assert resp.status_code == 401

    def test_get_without_token(self, client):
        resp = client.get("/books/1")
        assert resp.status_code == 401

    def test_update_without_token(self, client):
        resp = client.put("/books/1", json={"price": 20.0})
        assert resp.status_code == 401

    def test_delete_without_token(self, client):
        resp = client.delete("/books/1")
        assert resp.status_code == 401

    def test_search_without_token(self, client):
        resp = client.get("/books/search?q=test")
        assert resp.status_code == 401

    def test_stats_without_token(self, client):
        resp = client.get("/books/stats")
        assert resp.status_code == 401

    def test_valid_token_works(self, client):
        resp = client.post("/books", json=SAMPLE_BOOK, headers=AUTH_HEADERS)
        assert resp.status_code == 201
