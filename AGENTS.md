# AI-Sandbox — agent guide

## Scope

| Path | Treat as |
|------|----------|
| `source_codes/pageSense/` | **Active** — extension + FastAPI + Qdrant |
| `source_codes/agentForge/` | **Active** — smolagents + Gradio (HF course fork) |
| `archive/` | **Read-only reference** — do not “fix forward” unless the user asks to revive a project |

## Rules

- Do not refactor active app logic unless requested.
- Do not commit secrets, `data/`, or `qdrant_data/`.
- Do not restore basic tutorials (LangChain hello-agents, one-off caption scripts) without explicit user request.
- For PageSense local runs: `QDRANT_HOST=localhost`; Docker Compose continues to use `qdrant`.

## Index

- [README.md](./README.md)
- [source_codes/README.md](./source_codes/README.md)
- [archive/README.md](./archive/README.md)
