# PageSense backend

FastAPI service + Qdrant for embedding and searching Chrome history/bookmarks.

## Docker (recommended)

From `source_codes/pageSense/`:

```sh
docker compose up --build
```

- API: http://localhost:8000  
- Qdrant: port 6333  
- `QDRANT_HOST` is set to `qdrant` (Docker service name) in `docker-compose.yml`.

## Local Python (without Docker)

1. Run Qdrant locally (e.g. `docker run -p 6333:6333 qdrant/qdrant`) or use an existing instance.
2. Set environment before starting the API:

   ```sh
   # Windows PowerShell
   $env:QDRANT_HOST="localhost"
   $env:QDRANT_PORT="6333"

   # macOS / Linux
   export QDRANT_HOST=localhost
   export QDRANT_PORT=6333
   ```

3. Install and run:

   ```sh
   cd source_codes/pageSense/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The Chrome extension expects the API at `http://localhost:8000`.
