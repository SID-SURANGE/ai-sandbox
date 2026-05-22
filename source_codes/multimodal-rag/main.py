# Standard library imports
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
from pathlib import Path

# Local imports
from src.api.barista import router as barista_router
from src.api.data_loader import router as data_loader_router

APP_CONFIG = {
    "TEMP_DIR": "temp_uploads",
    "OUTPUT_TYPE": "html",
    "HOST": "127.0.0.1",
    "PORT": 8000,
}

# get constants
HOST = APP_CONFIG["HOST"]
PORT = APP_CONFIG["PORT"]

app = FastAPI(
    title="Multimodal RAG",
    description="Multimodal RAG",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directory exists and is absolute
data_dir = Path("data").resolve()
if not data_dir.exists():
    data_dir.mkdir(parents=True)

print(f"Static files directory: {data_dir}")

# Mount static files directory for serving images
app.mount("/data", StaticFiles(directory=str(data_dir), html=True), name="data")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "static_dir": str(data_dir)}

@app.get("/test-static/{filename}")
async def test_static_file(filename: str):
    """Test endpoint to check if a static file is accessible"""
    file_path = data_dir / filename
    if file_path.exists():
        # Try to serve the file directly
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="image/jpeg" if filename.lower().endswith(('.jpg', '.jpeg')) else "image/png"
        )
    return JSONResponse({
        "status": "error",
        "message": "File not found",
        "file_path": str(file_path)
    }, status_code=404)

@app.get("/list-static")
async def list_static_files():
    """List all files in the static directory"""
    files = []
    for file in data_dir.glob("*"):
        if file.is_file():
            files.append({
                "name": file.name,
                "size": file.stat().st_size,
                "url": f"/data/{file.name}"
            })
    return {"files": files}

# Include routers
app.include_router(barista_router, prefix="/api/v1")
app.include_router(data_loader_router, prefix="/api/v1")

if __name__ == "__main__":
    print(f"Starting server...")
    print(f"Static files are being served from: {data_dir}")
    print("Available routes:")
    print("- /health -> Health check")
    print("- /data/... -> Static file access")
    print("- /test-static/{filename} -> Test static file access")
    print("- /list-static -> List available static files")
    print("- /api/v1/... -> API endpoints")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
