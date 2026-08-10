"""
The LangGraph question-answering workflow:

    START -> retrieve -> generate -> END

GraphState flows through both nodes:
    question : the user's question (input)
    context  : retrieved document chunks (filled in by retrieve)
    answer   : the generated answer (filled in by generate)
"""
import os
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from rag.ingest import vector_store

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "3"))

# Llama 3.2, served locally by Ollama, is the model that generates answers.
llm = ChatOllama(model=LLM_MODEL, temperature=0)

PROMPT = ChatPromptTemplate.from_template(
    """You are a document assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context,
say that you do not know.

Context:
{context}

Question:
{question}"""
)


class GraphState(TypedDict):
    question: str
    context: list
    answer: str


def retrieve(state: GraphState) -> dict:
    """Node 1: Retriever searches Chroma for the chunks whose embeddings
    are most similar to the question's embedding (semantic search)."""
    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    documents = retriever.invoke(state["question"])
    return {"context": documents}


def generate(state: GraphState) -> dict:
    """Node 2: Builds the prompt from the retrieved context and calls
    Llama 3.2 through Ollama to produce the final answer."""
    context_text = "\n\n".join(doc.page_content for doc in state["context"])
    prompt = PROMPT.format(context=context_text, question=state["question"])
    response = llm.invoke(prompt)
    return {"answer": response.content}


def build_graph():
    """Wires the two nodes into the START -> retrieve -> generate -> END
    graph and compiles it into a runnable."""
    graph = StateGraph(GraphState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


qa_graph = build_graph()


def _to_page_number(raw_page) -> int | None:
    # PyPDFLoader pages are 0-indexed; TextLoader has no "page" metadata.
    return raw_page + 1 if isinstance(raw_page, int) else None


def run_qa(question: str):
    """Runs the compiled graph for one question and returns (answer, sources)."""
    result = qa_graph.invoke({"question": question, "context": [], "answer": ""})
    sources = [
        {
            "document": doc.metadata.get("source", "unknown"),
            "page": _to_page_number(doc.metadata.get("page")),
        }
        for doc in result["context"]
    ]
    return result["answer"], sources
