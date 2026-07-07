"""Query routes for searching text chunks."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.chat_service import add_message, create_session, get_history
from backend.services.llm_service import generate_answer
from backend.services.search_service import search_chunks
from backend.services.storage_service import load_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    """Request payload for chunk-based document querying."""

    filename: str
    query: str
    session_id: str | None = None


class MatchItem(BaseModel):
    """Public representation of a matched chunk."""

    chunk_id: int
    text: str


class QueryResponse(BaseModel):
    """Response payload for document query results."""

    session_id: str
    query: str
    answer: str
    matches: list[MatchItem]


@router.post("/query", response_model=QueryResponse)
async def query_chunks(request: QueryRequest) -> QueryResponse:
    """Return an answer and the top matching chunks for a stored document."""
    session_id = request.session_id or str(uuid4())

    try:
        chunks = load_chunks(request.filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Chunk file not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    try:
        create_session(session_id)
        add_message(session_id, "user", request.query)
        history = get_history(session_id)

        matched_chunks = search_chunks(request.query, chunks)
        context_chunks = [chunk["text"] for chunk in matched_chunks]
        answer = generate_answer(
            query=request.query,
            context_chunks=context_chunks,
            history=history,
        )
    except Exception as exc:
        if context_chunks := [chunk["text"] for chunk in matched_chunks if "text" in chunk]:
            answer = "Based on the uploaded document:\n\n" + "\n\n".join(context_chunks)
        else:
            answer = "I couldn't find relevant information in the uploaded document."

    try:
        add_message(session_id, "assistant", answer)
    except Exception:
        pass

    response_matches = [MatchItem(chunk_id=chunk["chunk_id"], text=chunk["text"]) for chunk in matched_chunks]
    return QueryResponse(session_id=session_id, query=request.query, answer=answer, matches=response_matches)
