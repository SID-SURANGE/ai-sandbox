# Archive

Projects moved here are **kept for reference** but are not maintained for 2026 toolchains. They may have broken README steps, unpinned dependencies, or APIs that have drifted (LangChain, LlamaIndex, LM Studio, etc.).

| Project | Archived | Why |
|---------|----------|-----|
| [multimodal-rag](./multimodal-rag/) | 2026-05 | No `requirements.txt`; README points at missing `src/ui.py`; text/PDF ingest disabled in code; needs LM Studio + Together setup |
| [chat-with-gitrepo](./chat-with-gitrepo/) | 2026-05 | Single-file LlamaIndex demo; default branch `master`; no pinned stack or explicit LLM/embed settings in app |

**Active development** lives under [`../source_codes/`](../source_codes/) (PageSense, AgentForge).

To revive a project: move it back to `source_codes/`, add a locked `requirements.txt`, update README run commands, and test on a clean venv.
