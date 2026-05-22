import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

from app.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME, VECTOR_SIZE
from app.utils.embeddings import generate_embeddings, generate_query_embedding
from app.models.schemas import PageData

# Initialize Qdrant client
client = None

def init_vector_db():
    """Initialize the Qdrant vector database."""
    global client
    
    try:
        # Initialize client with local mode for development
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Check if collection exists, create if it doesn't
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if QDRANT_COLLECTION_NAME not in collection_names:
            logging.info(f"Creating new Qdrant collection: {QDRANT_COLLECTION_NAME}")
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
        
        logging.info(f"Qdrant collection '{QDRANT_COLLECTION_NAME}' is ready")
        return True
    
    except Exception as e:
        logging.error(f"Error initializing Qdrant: {e}")
        return False

def add_pages(pages: List[PageData]) -> int:
    """Add pages to the vector database."""
    if not pages or client is None:
        return 0
    
    try:
        # Extract content for embedding
        contents = [page.content for page in pages]
        
        # Generate embeddings
        embeddings = generate_embeddings(contents)
        
        # Prepare points for Qdrant
        points = [
            PointStruct(
                id=i,  # Use a unique ID (you might want to use a hash of the URL for production)
                vector=embedding.tolist(),
                payload={
                    "url": page.url,
                    "title": page.title,
                    "content": page.content,
                    "type": page.type
                }
            )
            for i, (embedding, page) in enumerate(zip(embeddings, pages), start=len(get_all_ids()))
        ]
        
        # Add to Qdrant
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        
        logging.info(f"Added {len(points)} pages to Qdrant")
        return len(points)
    
    except Exception as e:
        logging.error(f"Error adding pages to Qdrant: {e}")
        return 0

def get_all_ids():
    """Get all IDs in the collection to avoid duplicates."""
    if client is None:
        return []
    
    try:
        # Get collection info to check the count
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        count = collection_info.vectors_count
        
        if count == 0:
            return []
        
        # Scroll through all points to get IDs
        result = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=count,
            with_vectors=False,
            with_payload=False
        )
        
        return [point.id for point in result[0]]
    
    except Exception as e:
        logging.error(f"Error getting IDs from Qdrant: {e}")
        return []

def search_vectors(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search the vector database for similar vectors."""
    if client is None:
        return []
    
    try:
        # Generate embedding for query
        query_embedding = generate_query_embedding(query)
        
        # Always limit to top 3 results
        search_results = client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=3
        )
        
        # Format results
        results = [
            {
                "url": result.payload.get("url"),
                "title": result.payload.get("title"),
                "type": result.payload.get("type"),
                "similarity_score": float(result.score)
            }
            for result in search_results
        ]
        
        return results
    
    except Exception as e:
        logging.error(f"Error searching in Qdrant: {e}")
        return []


def get_stats():
    """Get statistics about the vector database."""
    if client is None:
        return {"status": "error", "message": "Qdrant client not initialized"}
    try:
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        logging.info(f"Qdrant collection_info: {collection_info}")
        # Try both common attribute names
        total_vectors = getattr(collection_info, "vectors_count", None)
        if total_vectors is None:
            total_vectors = getattr(collection_info, "points_count", None)
        # Fallback: try to count points
        if total_vectors is None and hasattr(client, "count"):
            total_vectors = client.count(collection_name=QDRANT_COLLECTION_NAME)
        return {
            "status": "success",
            "total_vectors": total_vectors,
            "collection_name": QDRANT_COLLECTION_NAME
        }
    except Exception as e:
        logging.error(f"Error getting stats from Qdrant: {e}")
        return {"status": "error", "message": str(e)}

# def get_stats():
#     """Get statistics about the vector database."""
#     if client is None:
#         return {"status": "error", "message": "Qdrant client not initialized"}
    
#     try:
#         collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
#         logging.info(f"Qdrant collection_info: {collection_info}")
#         return {
#             "status": "success",
#             "total_vectors": collection_info.vectors_count,
#             "collection_name": QDRANT_COLLECTION_NAME
#         }
    
#     except Exception as e:
#         logging.error(f"Error getting stats from Qdrant: {e}")
#         return {"status": "error", "message": str(e)}
