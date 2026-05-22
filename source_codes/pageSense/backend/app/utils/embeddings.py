from sentence_transformers import SentenceTransformer
from app.config import MODEL_NAME

# Initialize the model
model = SentenceTransformer(MODEL_NAME)

def get_embedding_dimension():
    """Return the dimension of embeddings from the model."""
    return model.get_sentence_embedding_dimension()

def generate_embeddings(texts):
    """Generate embeddings for a list of texts."""
    embeddings = model.encode(texts, convert_to_tensor=False)
    return embeddings

def generate_query_embedding(query):
    """Generate embedding for a single query."""
    query_embedding = model.encode(query, convert_to_tensor=False)
    return query_embedding
