import pytest

import backend.services.search_service as search_service


def test_search_chunks_returns_top_matches_by_cosine_similarity(monkeypatch):
    monkeypatch.setattr(search_service, "generate_embedding", lambda text: [1.0, 0.0])

    stored_chunks = [
        {"chunk_id": 1, "text": "alpha", "embedding": [1.0, 0.0]},
        {"chunk_id": 2, "text": "beta", "embedding": [0.8, 0.6]},
        {"chunk_id": 3, "text": "gamma", "embedding": [0.0, 1.0]},
        {"chunk_id": 4, "text": "delta", "embedding": "not-a-vector"},
        {"chunk_id": 5, "text": "epsilon"},
    ]

    matches = search_service.search_chunks("alpha", stored_chunks, top_k=2)

    assert [item["chunk_id"] for item in matches] == [1, 2]
    assert [item["text"] for item in matches] == ["alpha", "beta"]


def test_search_chunks_falls_back_to_text_overlap_when_embedding_generation_fails(monkeypatch):
    monkeypatch.setattr(search_service, "generate_embedding", lambda text: (_ for _ in ()).throw(RuntimeError("boom")))

    stored_chunks = [
        {"chunk_id": 1, "text": "alpha", "embedding": [1.0, 0.0]},
        {"chunk_id": 2, "text": "beta", "embedding": [0.8, 0.6]},
    ]

    matches = search_service.search_chunks("alpha", stored_chunks, top_k=1)

    assert [item["chunk_id"] for item in matches] == [1]


def test_search_chunks_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        search_service.search_chunks("alpha", [], top_k=0)
