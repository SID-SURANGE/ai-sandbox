# Standard library imports
import logging
from typing import Dict, List, Optional
import numpy as np
import torch
from pathlib import Path

# Local imports
from utils.config import (
    collection,
    text_model,
    clip_model,
    clip_processor,
    device,
    cross_encoder
)

logger = logging.getLogger(__name__)

def query_db(query: str, limit: int = 5) -> List[Dict]:
    """
    Query the vector database for relevant results using both text and image models.
    
    Args:
        query (str): The search query
        limit (int): Maximum number of results to return
        
    Returns:
        List[Dict]: List of relevant results with their metadata
    """
    try:
        logger.info(f"Querying database with: {query}")
        
        # Get text embedding for text content
        text_query_embedding = text_model.encode(query).astype(np.float32)
        
        # Get CLIP embedding for image content
        clip_inputs = clip_processor(text=[query], return_tensors="pt", padding=True).to(device)
        
        with torch.no_grad():
            clip_features = clip_model.get_text_features(**clip_inputs)
            clip_features = clip_features / clip_features.norm(dim=-1, keepdim=True)
            clip_query_embedding = clip_features.cpu().numpy()[0].astype(np.float32)

        
        # Query ChromaDB twice - once for each content type
        text_results = collection.query(
            query_embeddings=[text_query_embedding.tolist()],
            where={"content_type": "text"},  # Filter for text content
            n_results=limit,
            include=["metadatas", "embeddings"]
        )
        
        image_results = collection.query(
            query_embeddings=[clip_query_embedding.tolist()],
            where={"content_type": "image"},  # Filter for image content
            n_results=limit,
            include=["metadatas", "embeddings"]
        )
        
        print("Debug - Image query results:")
        print(f"Number of image results: {len(image_results['ids'])}")
        print(f"Image metadatas: {image_results['metadatas']}")
        
        # Process text results
        all_results = []
        if text_results['ids']:
            for idx, embedding in enumerate(text_results['embeddings'][0]):
                meta = text_results['metadatas'][0][idx]
                # Calculate similarity using text model embeddings
                embedding = np.array(embedding, dtype=np.float32)  # Convert stored embedding to float32
                similarity = np.dot(text_query_embedding, embedding) / (
                    np.linalg.norm(text_query_embedding) * np.linalg.norm(embedding)
                )
                
                if similarity > 0.1:  # Threshold for text
                    all_results.append({
                        'content_type': 'text',
                        'content': meta.get('description', ''),
                        'file_path': meta.get('file_path', ''),
                        'filename': Path(meta.get('file_path', '')).name,
                        'similarity_score': float(similarity)
                    })
        
        # Process image results
        if image_results['ids']:
            for idx, embedding in enumerate(image_results['embeddings'][0]):
                meta = image_results['metadatas'][0][idx]
                print(f"Debug - Processing image result {idx}:")
                print(f"Metadata: {meta}")
                
                # Convert stored embedding to tensor for CLIP similarity
                embedding = np.array(embedding, dtype=np.float32)  # Convert to float32 first
                image_features = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0).to(device)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                # Calculate similarity using CLIP's dot product
                similarity = (100.0 * clip_features @ image_features.T).softmax(dim=-1)
                similarity_score = similarity.cpu().numpy()[0][0]
                
                if similarity_score > 0.03:  # Threshold for images
                    result = {
                        'content_type': 'image',
                        'file_path': meta.get('file_path', ''),  # This should be the URL path
                        'filename': meta.get('filename', ''),    # Use filename from metadata
                        'description': meta.get('description', ''),
                        'similarity_score': float(similarity_score)
                    }
                    print(f"Debug - Adding image result: {result}")
                    all_results.append(result)
        
        # Normalize similarity scores between content types
        if all_results:
            text_scores = [r['similarity_score'] for r in all_results if r['content_type'] == 'text']
            image_scores = [r['similarity_score'] for r in all_results if r['content_type'] == 'image']
            
            if text_scores:
                text_max = max(text_scores)
                for r in all_results:
                    if r['content_type'] == 'text':
                        r['similarity_score'] = r['similarity_score'] / text_max
            
            if image_scores:
                image_max = max(image_scores)
                for r in all_results:
                    if r['content_type'] == 'image':
                        r['similarity_score'] = r['similarity_score'] / image_max
        
        # Sort by normalized similarity score
        all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        print(f"Debug - Final results: {all_results}")
        return all_results[:limit]
        
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        return []