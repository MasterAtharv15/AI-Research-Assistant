import json

import pytest

import backend.services.storage_service as storage_service


def test_save_and_load_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    storage_service.save_chunks("sample.pdf", ["first chunk", "second chunk"])

    saved_path = tmp_path / "chunks" / "sample.json"
    assert saved_path.exists()
    payload = json.loads(saved_path.read_text(encoding="utf-8"))
    assert payload[0]["text"] == "first chunk"
    assert payload[0]["chunk_id"] == 0
    assert isinstance(payload[0]["embedding"], list)
    assert payload[1]["text"] == "second chunk"
    assert payload[1]["chunk_id"] == 1

    loaded = storage_service.load_chunks("sample.pdf")
    assert [item["text"] for item in loaded] == ["first chunk", "second chunk"]
    assert [item["chunk_id"] for item in loaded] == [0, 1]


def test_load_chunks_raises_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    with pytest.raises(FileNotFoundError):
        storage_service.load_chunks("missing.pdf")


def test_save_chunks_rejects_invalid_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    with pytest.raises(ValueError):
        storage_service.save_chunks("../bad.pdf", ["chunk"])
