# Standard library imports
import logging
# Third party imports
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse

# Local application imports
from src.model import run_llm
from src.context_engine import get_contextualized_llm_response

# Create a router for the parser endpoints
router = APIRouter(tags=["barista"])


class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = []

@router.post("/ask-barista-bot")
async def process_barista_query(request: QueryRequest) -> JSONResponse:
    """
    Process a user query and return a contextualized response.

    Args:
        request (QueryRequest): The query object containing the user's question and history.

    Returns:
        JSONResponse: The response containing the answer or error message.

    Raises:
        HTTPException: If the query is empty or invalid.
    """
    try:
        # Input validation
        query_text = request.query.strip()
        if not query_text:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )

        # Log incoming query for debugging
        logging.info(f"Processing query: {query_text}")

        # Get response from LLM
        response = await get_contextualized_llm_response(query_text)
        
        # Return response
        return JSONResponse(
            content={
                "status": "success",
                "response": {
                    "llm_response": response.get("llm_response", ""),
                    "display_results": response.get("display_results", []),
                    "query": query_text,
                }
            },
            status_code=200
        )

    except HTTPException as he:
        # Re-raise HTTP exceptions for proper error handling
        raise he

    except Exception as e:
        # Log the full error for debugging
        logging.error(f"Error processing query: {str(e)}", exc_info=True)
        
        return JSONResponse(
            content={
                "status": "error",
                "response": "An error occurred while processing your request",
                "error_type": "internal_server_error"
            },
            status_code=500
        )
