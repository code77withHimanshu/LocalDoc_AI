"""
FastAPI app for the LocalDoc AI Python AI service.

Endpoints:
    POST /documents  - upload + ingest a PDF/TXT file into Chroma
    GET  /documents   - list previously uploaded documents
    POST /chat        - run the LangGraph question-answering workflow
    GET  /health       - simple liveness check
"""
import os
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, DocumentsResponse, UploadResponse
from rag.graph import run_qa
from rag.ingest import DOCUMENTS_DIR, ingest_document, list_uploaded_documents

app = FastAPI(title="LocalDoc AI - Python AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = (".pdf", ".txt")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/documents", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    try:
        chunk_count = ingest_document(file_path, file.filename)
    except Exception as exc:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {exc}") from exc

    return UploadResponse(filename=file.filename, chunks=chunk_count)


@app.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    return DocumentsResponse(documents=list_uploaded_documents())


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    if not list_uploaded_documents():
        raise HTTPException(status_code=400, detail="No documents uploaded yet")

    try:
        answer, sources = run_qa(request.question)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI generation failed: {exc}. Is Ollama running with the required models pulled?",
        ) from exc

    return ChatResponse(answer=answer, sources=sources)
