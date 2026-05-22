from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from app.models.schemas import PageData, QueryRequest, SearchResponse, StatusResponse
from app.database.vector_store import add_pages, search_vectors, get_stats

router = APIRouter()

@router.post("/index_pages", response_model=StatusResponse)
async def index_pages(pages: List[PageData]):
    """Index pages in the vector database."""
    try:
        indexed_count = add_pages(pages)
        return {
            "status": "success",
            "indexed_count": indexed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing pages: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search(query_request: QueryRequest):
    """Search for pages similar to the query."""
    try:
        results = search_vectors(query_request.query, query_request.limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

@router.get("/stats")
async def get_db_stats():
    """Get statistics about the vector database."""
    return get_stats()
