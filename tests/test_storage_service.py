import json

import pytest

import backend.services.storage_service as storage_service


def test_save_and_load_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    storage_service.save_chunks("sample.pdf", ["first chunk", "second chunk"])

    saved_path = tmp_path / "chunks" / "sample.json"
    assert saved_path.exists()
    assert json.loads(saved_path.read_text(encoding="utf-8")) == ["first chunk", "second chunk"]
    assert storage_service.load_chunks("sample.pdf") == ["first chunk", "second chunk"]


def test_load_chunks_raises_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    with pytest.raises(FileNotFoundError):
        storage_service.load_chunks("missing.pdf")


def test_save_chunks_rejects_invalid_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "_chunk_storage_dir", lambda: tmp_path / "chunks")

    with pytest.raises(ValueError):
        storage_service.save_chunks("../bad.pdf", ["chunk"])
