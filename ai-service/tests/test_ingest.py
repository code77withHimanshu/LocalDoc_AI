"""Tests for the Document Loader + Text Splitter steps of the pipeline.

These stay offline: load_document/split_documents never touch embeddings
or Ollama, so no local model needs to be running to test them.
"""
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
