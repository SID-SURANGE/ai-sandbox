from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from app.routers import search
from app.database.vector_store import init_vector_db
from app.config import CORS_ORIGINS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logging.info("Initializing vector database")
    init_vector_db()
    
    yield
    
    # Shutdown code
    logging.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title="PageBrain API",
    description="API for semantic search over browsing history and bookmarks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Include routers
app.include_router(search.router, tags=["search"])

# Root endpoint
@app.get("/", tags=["status"])
async def root():
    return {"status": "online", "message": "PageBrain API is running"}
