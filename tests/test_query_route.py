from fastapi.testclient import TestClient

from backend.main import app
from backend.routes import query as query_route
from backend.services import storage_service


client = TestClient(app)


def test_query_route_returns_answer_and_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")
    storage_service.save_chunks("sample.pdf", ["alpha beta", "gamma delta"])

    response = client.post(
        "/query",
        json={"filename": "sample.pdf", "query": "alpha"},
    )

    assert response.status_code == 200
    assert response.json()["answer"].startswith("Based on the uploaded document")
    assert response.json()["matches"] == ["alpha beta"]


def test_query_route_returns_404_for_missing_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    response = client.post(
        "/query",
        json={"filename": "missing.pdf", "query": "alpha"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chunk file not found"


def test_query_route_returns_query_and_matches_in_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")
    storage_service.save_chunks("sample.pdf", ["alpha beta", "gamma delta"])

    response = client.post(
        "/query",
        json={"filename": "sample.pdf", "query": "alpha"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "alpha",
        "answer": "Based on the uploaded document:\n\nalpha beta",
        "matches": ["alpha beta"],
    }


def test_query_route_returns_500_for_unexpected_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")
    monkeypatch.setattr(query_route, "load_chunks", lambda _filename: (_ for _ in ()).throw(RuntimeError("boom")))

    response = client.post(
        "/query",
        json={"filename": "sample.pdf", "query": "alpha"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
