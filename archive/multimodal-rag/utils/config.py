from sentence_transformers import SentenceTransformer, CrossEncoder
from chromadb import PersistentClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import CLIPProcessor, CLIPModel
import torch

# Initialize cross-encoder model for more accurate result ranking
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Define collection schema
collection_schema = {
    "text": {
        "document": str,
        "embedding": list,
        "metadata": {
            "type": "text",
            "filename": str
        }
    },
    "image": {
        "image_path": str,
        "embedding": list,
        "metadata": {
            "type": "image",
            "filename": str,
            "description": str
        },
    },
    "video": {
        "video_path": str,
        "embedding": list,
        "metadata": {
            "type": "video",
            "filename": str,
            "duration": float,
            "frames": {
                "timestamp": float,
                "frame_embedding": list,
                "frame_description": str
            },
            "audio": {
                "transcript": str,
                "transcript_embedding": list,
                "segments": [{
                    "start": float,
                    "end": float,
                    "text": str
                }]
            }
        }
    },
    "audio": {
        "audio_path": str,
        "embedding": list,
        "metadata": {
            "type": "audio",
            "filename": str,
            "description": str
        }
    }
}

collection_schema_unified = {
    "document": {
        "content_path": str,     # Works for all file types
        "embedding": list,       # CLIP embeddings (same dimension for all)
        "metadata": {
            "type": str,         # "text", "image", "video", "audio"
            "filename": str,     # Original filename
            "description": str,  # Can store:
                                # - Text chunks for documents
                                # - Image captions
                                # - Video frame descriptions
                                # - Audio transcriptions
            "keywords": list     # Can store:
                                # - Key terms from text
                                # - Image tags
                                # - Video scene labels
                                # - Audio segment keywords
        }
    }
}

# Initialize ChromaDB Client
client = PersistentClient(path="./chromadb")
collection = client.get_or_create_collection(name="multimodal_data_new")

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# Model Configuration
text_model = SentenceTransformer("all-mpnet-base-v2")
# image_model = SentenceTransformer("clip-ViT-L-14")
# unified_model = SentenceTransformer("clip-ViT-L-14")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = clip_model.to(device)

# Constants
FIXED_DIMENSION = 768
