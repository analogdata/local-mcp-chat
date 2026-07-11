class TestHealthAndRoot:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "Books ERP API"
        assert "docs" in data

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}

    def test_root_no_auth_required(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_health_no_auth_required(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
