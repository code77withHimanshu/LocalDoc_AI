"""
The LangChain ingestion pipeline:

    PDF / TXT
       v
    Document Loader   (PyPDFLoader / TextLoader)
       v
    Text Splitter      (RecursiveCharacterTextSplitter)
       v
    Embeddings         (OllamaEmbeddings)
       v
    Vector Store        (Chroma)

Each step below is kept as its own small function so the pipeline stays
explicit instead of hiding behind a single framework call.
"""
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Chunking defaults, kept configurable via env vars.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Ollama does not have to serve the same model for chat and embeddings.
# Llama 3.2 is a general-purpose chat model; nomic-embed-text is a small
# model trained specifically to produce good embedding vectors, so we use
# it instead of asking Llama 3.2 to do a job it wasn't tuned for.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_data")
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./uploaded_docs")
COLLECTION_NAME = "localdoc"

# CHROMA_SERVER_HOST is only set in docker-compose, where Chroma runs as
# its own container. For local development (`uvicorn main:app`), Chroma
# just persists to a folder on disk - no separate server needed.
CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST")
CHROMA_SERVER_PORT = int(os.getenv("CHROMA_SERVER_PORT", "8000"))

# Embeddings turn text into vectors so semantically similar text ends up
# close together in vector space.
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

# Chroma is the local vector database that stores chunk embeddings and lets
# us search them later by similarity.
if CHROMA_SERVER_HOST:
    import chromadb

    chroma_client = chromadb.HttpClient(host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT)
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        client=chroma_client,
    )
else:
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


def load_document(file_path: str, filename: str):
    """Document Loader: reads a PDF or text file into LangChain Documents."""
    if filename.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def split_documents(documents):
    """Text Splitter: breaks long documents into overlapping chunks so each
    chunk is small enough to embed meaningfully and fit in the LLM prompt."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def ingest_document(file_path: str, filename: str) -> int:
    """Runs the full ingestion pipeline for one uploaded file and returns
    the number of chunks stored in the vector store."""
    documents = load_document(file_path, filename)
    for doc in documents:
        doc.metadata["source"] = filename

    chunks = split_documents(documents)
    vector_store.add_documents(chunks)
    return len(chunks)


def list_uploaded_documents() -> list[str]:
    """Returns filenames already stored on disk, so the document list
    survives a service restart without needing a separate database."""
    if not os.path.isdir(DOCUMENTS_DIR):
        return []
    return sorted(os.listdir(DOCUMENTS_DIR))


def delete_document(filename: str) -> bool:
    """Removes a document's chunks from Chroma (matched by the "source"
    metadata set during ingestion) and deletes its file from disk. Returns
    False if the document doesn't exist."""
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.isfile(file_path):
        return False

    vector_store.delete(where={"source": filename})
    os.remove(file_path)
    return True
