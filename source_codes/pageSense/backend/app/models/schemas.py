from pydantic import BaseModel
from typing import List, Optional

class PageData(BaseModel):
    url: str
    title: str
    content: str
    type: str  # 'history' or 'bookmark'

class QueryRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    url: str
    title: str
    type: str
    similarity_score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    indexed_count: Optional[int] = None
