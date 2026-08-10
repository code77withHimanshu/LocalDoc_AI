"""Tests for retrieval against Chroma.

Uses a fake, deterministic embeddings implementation instead of
OllamaEmbeddings so the test suite runs without a local Ollama server.
"""
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class FakeEmbeddings(Embeddings):
    """Deterministic stand-in for OllamaEmbeddings."""

    def embed_documents(self, texts):
        return [[float(len(text) % 7), float(text.count("a"))] for text in texts]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def test_retriever_returns_top_k_chunks(tmp_path):
    store = Chroma(
        collection_name="test-collection",
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
    )
    store.add_documents(
        [
            Document(page_content="apple banana", metadata={"source": "a.txt"}),
            Document(page_content="car engine", metadata={"source": "b.txt"}),
            Document(page_content="apple pie recipe", metadata={"source": "c.txt"}),
        ]
    )

    retriever = store.as_retriever(search_kwargs={"k": 2})
    results = retriever.invoke("apple")

    assert len(results) == 2
