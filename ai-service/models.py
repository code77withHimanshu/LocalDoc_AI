"""Pydantic request/response schemas shared by the FastAPI routes."""
from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    document: str
    page: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


class UploadResponse(BaseModel):
    filename: str
    chunks: int


class DocumentsResponse(BaseModel):
    documents: List[str]
