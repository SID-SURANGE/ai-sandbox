# source_codes

**Active** projects only. Archived experiments (multimodal RAG, GitHub chat) were moved to [`../archive/`](../archive/).

## Projects

| Folder | Status | Run instructions |
|--------|--------|------------------|
| `pageSense/` | **Active** | [pageSense/README.md](./pageSense/README.md) — extension + [backend/README.md](./pageSense/backend/README.md) |
| `agentForge/` | **Active** (course demo) | [agentForge/README.md](./agentForge/README.md) — needs OpenAI + Hugging Face tokens |

## Conventions

- One virtual environment per project; install from that project’s `requirements.txt`.
- Do not commit `.env`, `data/`, or `qdrant_data/`.
- PageSense: prefer `docker compose` from `pageSense/`; for local API + Qdrant set `QDRANT_HOST=localhost`.

## Removed from repo (2026 cleanup)

- **`LLM-Agents-tutorials/`** — introductory LangChain email agent only; not worth keeping in the sandbox.
- **`image-captioning/`** — two standalone caption scripts (Together + SmolVLM); too basic for this repo.

History for deleted folders may still exist in older git commits.
