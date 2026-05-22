# AI-Sandbox

Personal monorepo for AI experiments. **Maintained apps** live under [`source_codes/`](./source_codes/). Older or broken demos are in [`archive/`](./archive/) for reference only.

**Default branch:** `dev`

## Active projects

| Project | Description | Docs |
|---------|-------------|------|
| [PageSense](./source_codes/pageSense/) | Chrome extension + FastAPI/Qdrant semantic search for history and bookmarks | [README](./source_codes/pageSense/README.md) |
| [AgentForge](./source_codes/agentForge/) | Gradio + smolagents assistant (HF Agent Course fork; web search + image gen) | [README](./source_codes/agentForge/README.md) |

## Archive (not maintained for 2026)

| Project | Notes |
|---------|--------|
| [multimodal-rag](./archive/multimodal-rag/) | Streamlit + FastAPI barista RAG — README and deps out of sync when archived |
| [chat-with-gitrepo](./archive/chat-with-gitrepo/) | LlamaIndex GitHub chat demo — unpinned stack, `master` default branch |

See [archive/README.md](./archive/README.md) before trying to run archived code.

## Quick start

```sh
git clone https://github.com/SID-SURANGE/AI-Sandbox.git
cd AI-Sandbox
git checkout dev
```

Pick a project from the table, open its README, create a venv, and install that folder’s `requirements.txt`. Copy [`.env.example`](./.env.example) to `.env` when the project needs API keys.

## Layout

```
AI-Sandbox/
├── source_codes/     # Active applications
├── archive/          # Frozen experiments (reference only)
├── notebooks/        # Local Jupyter work (gitignored)
├── AGENTS.md
├── .env.example
└── README.md
```

## Notebooks

`notebooks/` is gitignored. Nothing under `source_codes/` depends on it.

## Agents & license

- [AGENTS.md](./AGENTS.md) — monorepo rules for Cursor / coding agents  
- [MIT License](./LICENSE)
