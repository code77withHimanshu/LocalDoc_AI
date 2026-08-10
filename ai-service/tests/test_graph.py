"""Tests for the LangGraph workflow: START -> retrieve -> generate -> END.

The retriever and the LLM are monkeypatched so the graph can be exercised
end to end without a running Ollama server.
"""
from langchain_core.documents import Document

import rag.graph as graph_module


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeRetriever:
    def __init__(self, docs):
        self._docs = docs

    def invoke(self, question):
        return self._docs


class FakeLLM:
    def invoke(self, prompt):
        return FakeResponse("It is a RAG demo project.")


def test_build_graph_has_retrieve_and_generate_nodes():
    compiled = graph_module.build_graph()
    nodes = compiled.get_graph().nodes

    assert "retrieve" in nodes
    assert "generate" in nodes


def test_run_qa_returns_answer_and_sources(monkeypatch):
    fake_docs = [
        Document(
            page_content="LocalDoc AI is a small local RAG demo.",
            metadata={"source": "sample.txt", "page": 0},
        )
    ]
    monkeypatch.setattr(
        graph_module.vector_store, "as_retriever", lambda **kwargs: FakeRetriever(fake_docs)
    )
    monkeypatch.setattr(graph_module, "llm", FakeLLM())

    answer, sources = graph_module.run_qa("What is LocalDoc AI?")

    assert answer == "It is a RAG demo project."
    assert sources == [{"document": "sample.txt", "page": 1}]
