"""Tests for the Document Loader + Text Splitter steps of the pipeline.

These stay offline: load_document/split_documents never touch embeddings
or Ollama, so no local model needs to be running to test them.
"""
import rag.ingest as ingest_module
from rag.ingest import load_document, split_documents


def test_load_document_reads_text_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("LocalDoc AI is a small RAG demo project.", encoding="utf-8")

    documents = load_document(str(file_path), "sample.txt")

    assert len(documents) == 1
    assert "LocalDoc AI" in documents[0].page_content


def test_split_documents_breaks_long_text_into_multiple_chunks(tmp_path):
    file_path = tmp_path / "long.txt"
    file_path.write_text("word " * 500, encoding="utf-8")

    documents = load_document(str(file_path), "long.txt")
    chunks = split_documents(documents)

    assert len(chunks) > 1
    assert all(chunk.page_content for chunk in chunks)


def test_delete_document_removes_file_and_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_module, "DOCUMENTS_DIR", str(tmp_path))
    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello world", encoding="utf-8")

    delete_calls = {}
    monkeypatch.setattr(
        ingest_module.vector_store, "delete", lambda **kwargs: delete_calls.update(kwargs)
    )

    result = ingest_module.delete_document("doc.txt")

    assert result is True
    assert not file_path.exists()
    assert delete_calls == {"where": {"source": "doc.txt"}}


def test_delete_document_returns_false_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_module, "DOCUMENTS_DIR", str(tmp_path))

    assert ingest_module.delete_document("missing.txt") is False
