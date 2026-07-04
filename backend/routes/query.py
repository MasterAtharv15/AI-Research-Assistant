"""Query routes for searching text chunks."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.search_service import search_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    chunks: list[str]


class QueryResponse(BaseModel):
    matches: list[str]


@router.post("/query", response_model=QueryResponse)
async def query_chunks(request: QueryRequest) -> QueryResponse:
    """Return the top matching chunks for a query."""
    matches = search_chunks(request.chunks, request.query)
    return QueryResponse(matches=matches)
