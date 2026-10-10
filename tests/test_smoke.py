from fastapi.testclient import TestClient

from app.main import app


# Card 1.2b replaces this with the `client` fixture from conftest.py.
def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
