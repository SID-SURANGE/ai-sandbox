# Standard library imports
from pathlib import Path
import logging
import numpy as np
import uuid
import torch

# Third-party imports
from PIL import Image

# Local imports
from utils.config import collection, clip_model, clip_processor, device
from src.model import run_caption_model

logger = logging.getLogger(__name__)

def generate_id(prefix: str, filename: str) -> str:
    """Generate a unique ID for an image."""
    return f"{prefix}_{Path(filename).stem}_{uuid.uuid4().hex[:8]}"

def process_image(file_path):
    """Process an image file, generate embeddings using CLIP, and store in ChromaDB."""
    try:
        print(f"Processing image file: {file_path}\n")
        
        # Validate file exists
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
            
        # Try opening and validating image
        try:
            image = Image.open(file_path)
            image.verify()  # Verify it's a valid image
            image = Image.open(file_path)  # Reopen image after verification
            
            # Convert image to RGB mode if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image file: {str(e)}")

        # Generate image embedding using CLIP
        try:
            # Process image for CLIP
            inputs = clip_processor(images=image, return_tensors="pt").to(device)
            
            # Get image features
            with torch.no_grad():
                image_features = clip_model.get_image_features(**inputs)
                
            # Convert to numpy and normalize
            embedding = image_features.cpu().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate image embedding: {str(e)}")

        # Generate image caption with fallback for errors
        try:
            caption_data = run_caption_model(image, str(file_path))
            print(f'Generated caption data: {caption_data} and its type {type(caption_data)}')
            
            # Handle case where caption_data is an error string
            if isinstance(caption_data, str):
                logger.warning(f"Caption model returned error string: {caption_data}")
                description = "No description available"
                keywords = ""
            # Handle Pydantic model case
            elif hasattr(caption_data, 'description'):
                description = caption_data.description
                keywords = ", ".join(caption_data.keywords) if caption_data.keywords else ""
            # Handle dictionary case
            elif isinstance(caption_data, dict):
                description = caption_data.get('description', 'No description available')
                keywords = ", ".join(caption_data.get('keywords', [])) if caption_data.get('keywords') else ""
            else:
                logger.warning(f"Unexpected caption data type: {type(caption_data)}")
                description = "No description available"
                keywords = ""
                
        except Exception as e:
            logger.warning(f"Failed to generate image caption for {file_path}: {str(e)}")
            description = "No description available"
            keywords = ""

        # Generate unique ID
        image_id = generate_id("img", str(file_path))

        # Convert to relative URL path for static file serving
        relative_path = file_path.name  # Just use the filename since all files are in data directory
        url_path = f"/data/{relative_path}"  # This will match the FastAPI static file mount point

        # Print debug information
        print(f"Debug - Processing image:")
        print(f"Original path: {file_path}")
        print(f"URL path: {url_path}")
        print(f"Filename: {file_path.name}")

        # Add to ChromaDB using unified schema
        metadata = {
            "content_type": "image",
            "file_path": url_path,  # Store the URL path instead of file path
            "filename": file_path.name,
            "description": description,
            "keywords": keywords  # Now a comma-separated string
        }
        print(f"Debug - Metadata being stored: {metadata}")

        try:
            collection.add(
                documents=[str(file_path)],  # Keep original file path as document
                embeddings=[embedding.tolist()],  # Store CLIP embedding
                metadatas=[metadata],
                ids=[image_id]
            )
            
            print(f"Successfully added image to ChromaDB with ID: {image_id}")
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to add image to ChromaDB: {str(e)}")

    except Exception as e:
        logger.error(f"Error processing image {file_path}: {str(e)}")
        print(f"Failed to process image {file_path}: {str(e)}")
        return False

    finally:
        # Clean up if needed
        if 'image' in locals():
            image.close()
