from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_history_returns_200():
    response = client.get("/history", params={"user_email": "demo@example.com"})
    assert response.status_code == 200


def test_delete_history_item():
    response = client.delete("/history/1")
    assert response.status_code == 200
    assert response.json() == {"deleted": 1}
