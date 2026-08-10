# LocalDoc AI

A small, educational document question-answering app built to learn **Ollama, Llama 3.2, LangChain, LangGraph, RAG, embeddings, and vector databases** — end to end, across a React + Spring Boot + FastAPI stack. It is intentionally small: no cloud APIs, no auth, no message queues, no Kubernetes.

---

## 1. What is the project?

You upload a small PDF or text file. The app chunks it, embeds the chunks, and stores them in a local vector database (Chroma). You then ask questions about the document in a chat UI. A LangGraph workflow retrieves the most relevant chunks and asks a locally-running Llama 3.2 model (via Ollama) to answer using only that context. The answer is shown along with the source chunks it came from.

Nothing leaves your machine — there is no cloud LLM call anywhere in this project.

---

## 2. Architecture

```text
React.js  (upload UI, chat UI)
   |  HTTP (axios)
   v
Spring Boot  (thin API layer: /api/documents, /api/chat)
   |  HTTP (RestTemplate)
   v
FastAPI  (the AI service - all the LangChain/LangGraph logic lives here)
   |
   +-- LangChain  (load -> split -> embed -> store -> retrieve -> prompt -> LLM)
   +-- LangGraph  (retrieve -> generate workflow)
   |
   +-- Chroma   (local vector database)
   +-- Ollama -> Llama 3.2   (local LLM, runs on the host machine)
```

Spring Boot has **no AI logic** — it only validates requests and forwards them. All RAG/LangChain/LangGraph work happens in the Python service. This mirrors a common real-world pattern: a JVM backend that talks to a specialized Python AI microservice instead of reimplementing AI tooling in Java.

---

## 3. Setup

### Prerequisites
- Python 3.11+
- Java 17+ and Maven
- Node.js 18+
- [Ollama](https://ollama.com) installed and running locally

### 3.1 Install and pull Ollama models

```bash
ollama serve            # if not already running
ollama pull llama3.2         # the chat/generation model
ollama pull nomic-embed-text  # the embedding model
```

**Why a different embedding model than Llama 3.2?** Llama 3.2 is a general-purpose chat model, not trained to produce high-quality embedding vectors. `nomic-embed-text` is a small model built specifically for embeddings — it's faster and gives better retrieval quality than repurposing a chat model for that job. This is standard practice even with cloud providers (e.g. OpenAI ships separate chat and embedding models too).

### 3.2 Python AI service

```bash
cd ai-service
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/health` -> `{"status":"ok"}`

### 3.3 Spring Boot backend

```bash
cd backend
mvn spring-boot:run
```

Runs on `http://localhost:8080`. It forwards to the AI service URL set in `application.properties` (`ai.service.url`, default `http://localhost:8000`).

### 3.4 React frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

### 3.5 Docker Compose (optional)

```bash
docker compose up --build
```

This runs `frontend`, `backend`, `ai-service`, and a `chroma` server container together. Ollama is **not** containerized — keep it running on the host; the AI service reaches it via `host.docker.internal`.

---

## 4. How RAG works

```text
Upload
  v
Load      - PyPDFLoader (.pdf) / TextLoader (.txt) reads the file into LangChain Documents
  v
Chunk     - RecursiveCharacterTextSplitter splits into ~500-char chunks, 50-char overlap
  v
Embed     - OllamaEmbeddings (nomic-embed-text) turns each chunk into a vector
  v
Store     - Chroma persists the vectors + chunk text + metadata (source filename, page)
  v
Retrieve  - given a question, embed it and find the top-k (k=3) most similar chunks
  v
Generate  - stuff those chunks into a prompt and ask Llama 3.2 to answer from them only
```

`chunk_size`, `chunk_overlap`, and `k` are all configurable via environment variables in `ai-service/rag/ingest.py` and `ai-service/rag/graph.py`.

---

## 5. How LangChain is used

Every stage of the pipeline is an explicit, separately-callable LangChain component (see `ai-service/rag/ingest.py` and `ai-service/rag/graph.py`):

| Stage | LangChain component |
|---|---|
| Document Loader | `PyPDFLoader`, `TextLoader` |
| Text Splitter | `RecursiveCharacterTextSplitter` |
| Embeddings | `OllamaEmbeddings` |
| Vector Store | `Chroma` (`langchain_chroma`) |
| Retriever | `vector_store.as_retriever(search_kwargs={"k": 3})` |
| Prompt Template | `ChatPromptTemplate.from_template(...)` |
| LLM | `ChatOllama` |

Nothing is hidden behind a single "magic" chain call — you can trace each arrow in the diagram above directly to a function.

---

## 6. How LangGraph is used

```text
State: { question, context, answer }

START
  v
retrieve   - searches Chroma, fills state["context"]
  v
generate   - builds the prompt from context, calls Llama 3.2, fills state["answer"]
  v
END
```

See `ai-service/rag/graph.py`:

```python
class GraphState(TypedDict):
    question: str
    context: list
    answer: str

graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
```

This is deliberately the simplest possible graph — two nodes, no branching, no loops, no agents — to make the core LangGraph concepts (state, nodes, edges, compiling, invoking) easy to see without extra machinery.

---

## 7. Example API calls

```bash
# Upload a document (through Spring Boot)
curl -X POST http://localhost:8080/api/documents \
  -F "file=@sample-documents/sample.txt"

# List uploaded documents
curl http://localhost:8080/api/documents

# Ask a question
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main purpose of this document?"}'
```

Example chat response:

```json
{
  "answer": "The document explains that LocalDoc AI is an educational RAG demo...",
  "sources": [
    { "document": "sample.txt", "page": null }
  ]
}
```

---

## 8. How I would explain this project in an interview

"LocalDoc AI is a small RAG application I built to learn how retrieval-augmented generation and LangGraph work in practice, without relying on any cloud LLM API. It's a three-tier stack: a React frontend, a Spring Boot API layer, and a Python FastAPI service that does all the AI work.

When a user uploads a document, the Python service loads it with LangChain, splits it into overlapping chunks, embeds each chunk with a local embedding model served by Ollama, and stores the vectors in Chroma, a local vector database. When the user asks a question, I run a LangGraph workflow with two nodes: a `retrieve` node that does a similarity search against Chroma for the top-3 relevant chunks, and a `generate` node that stuffs those chunks into a prompt and asks Llama 3.2 — also running locally through Ollama — to answer using only that context. The graph's state is a typed dict carrying the question, the retrieved context, and the final answer as it flows through the two nodes.

Spring Boot deliberately has no AI logic — it just validates requests and forwards them to the Python service, which is a realistic pattern for teams that want a JVM-based API layer in front of a specialized Python AI microservice. I kept the whole project intentionally small — no auth, no message queues, no cloud services — so I could focus entirely on understanding the RAG and LangGraph mechanics rather than infrastructure."

---

## 9. Important concepts

- **LLM (Large Language Model)** — a model trained to predict/generate text; here, Llama 3.2 generates answers.
- **Ollama** — a tool that runs LLMs locally on your machine and exposes them over a simple local API.
- **Llama 3.2** — the open-weight chat model used for answer generation in this project.
- **Embeddings** — numeric vectors that represent the meaning of text; similar meanings produce vectors that are close together.
- **Vector database** — a database (Chroma, here) optimized for storing embeddings and finding the nearest ones to a query vector.
- **Semantic search** — searching by meaning (via embedding similarity) instead of exact keyword matching.
- **RAG (Retrieval-Augmented Generation)** — retrieving relevant text and feeding it into an LLM prompt so the model can answer using facts it wasn't necessarily trained on.
- **LangChain** — a framework providing standard building blocks (loaders, splitters, retrievers, prompt templates, LLM wrappers) for building LLM applications.
- **LangGraph** — a framework for defining LLM application logic as an explicit graph of state-transforming nodes, rather than a single opaque chain call.
- **Graph state** — the typed data structure that flows through a LangGraph graph, read and updated by each node.
- **Nodes** — individual functions in a LangGraph graph, each transforming the state (here: `retrieve`, `generate`).
- **Edges** — the connections that define execution order between nodes, including the special `START` and `END` markers.

---

## 10. Testing

```bash
# Python
cd ai-service
pytest

# Spring Boot
cd backend
mvn test

# React
cd frontend
npm test
```

These are intentionally basic (document ingestion, retrieval, graph execution, controller behavior, and a couple of key components) — not exhaustive coverage.

---

## 11. Final project structure

```text
LocalDoc_AI/
|
|-- frontend/                  React (JS/JSX, Vite)
|   |-- src/components/        DocumentUpload, DocumentList, ChatWindow, ChatMessage, SourceList
|   |-- src/services/api.js
|   +-- src/App.jsx
|
|-- backend/                   Spring Boot (Java 17)
|   +-- src/main/java/com/localdocai/backend/
|       |-- controller/        DocumentController, ChatController
|       |-- service/           AiServiceClient
|       |-- dto/
|       +-- config/            WebConfig (CORS, RestTemplate)
|
|-- ai-service/                FastAPI (Python)
|   |-- main.py                routes
|   |-- models.py              pydantic schemas
|   +-- rag/
|       |-- ingest.py          Loader -> Splitter -> Embeddings -> Chroma
|       +-- graph.py           LangGraph: retrieve -> generate
|
|-- sample-documents/
|   +-- sample.txt
|
|-- docker-compose.yml
+-- README.md
```

## 12. How to run it (quick reference)

1. `ollama serve` + `ollama pull llama3.2` + `ollama pull nomic-embed-text`
2. `cd ai-service && uvicorn main:app --reload --port 8000`
3. `cd backend && mvn spring-boot:run`
4. `cd frontend && npm run dev`
5. Open `http://localhost:5173`, upload `sample-documents/sample.txt`, ask a question.

## 13. Example questions to ask the sample document

- "What is the main purpose of this document?"
- "What does LocalDoc AI do?"
- "Why does LocalDoc AI use local models instead of cloud AI providers?"
- "How does the Python service fit into the architecture?"

## 14. LangChain concepts demonstrated

Document loaders, text splitting/chunking, embeddings, vector stores, retrievers, prompt templates, and LLM invocation via a chat model wrapper.

## 15. LangGraph concepts demonstrated

Typed graph state, defining nodes as plain functions, wiring nodes with edges, `START`/`END`, compiling a graph, and invoking a compiled graph.

## 16. What to learn next

- Add a metadata filter to retrieval (e.g. restrict search to one uploaded document).
- Try a different chunking strategy (semantic chunking) and compare answer quality.
- Add a third LangGraph node, e.g. a "grade documents" step that decides whether retrieved context is actually relevant before generating.
- Swap Chroma for another local vector store (e.g. FAISS) to see how little application code needs to change.
- Stream the LLM's answer token-by-token to the frontend instead of waiting for the full response.
