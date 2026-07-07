"""Query routes for searching text chunks."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.answer_service import generate_answer
from backend.services.search_service import search_chunks
from backend.services.storage_service import load_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    """Request payload for chunk-based document querying."""

    filename: str
    query: str


class QueryResponse(BaseModel):
    """Response payload for document query results."""

    query: str
    answer: str
    matches: list[str]


@router.post("/query", response_model=QueryResponse)
async def query_chunks(request: QueryRequest) -> QueryResponse:
    """Return an answer and the top matching chunks for a stored document."""
    try:
        chunks = load_chunks(request.filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Chunk file not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    try:
        matches = search_chunks(chunks, request.query)
        answer = generate_answer(request.query, matches)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return QueryResponse(query=request.query, answer=answer, matches=matches)
