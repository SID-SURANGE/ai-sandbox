import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API settings
CORS_ORIGINS = ["chrome-extension://*"]

# Embedding model settings
MODEL_NAME = "all-MiniLM-L6-v2"

# Qdrant settings
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "page_embeddings"
VECTOR_SIZE = 384  # for all-MiniLM-L6-v2
