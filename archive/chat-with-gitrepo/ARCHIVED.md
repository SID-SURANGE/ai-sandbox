# Archived — chat-with-gitrepo

**Status:** Not maintained. Streamlit + LlamaIndex + Chroma demo for chatting with a public GitHub repo.

**Known gaps when archived:**

- Default git branch is `master` (many repos use `main`)
- `requirements.txt` unpinned; LlamaIndex ≥ 0.10 usually needs explicit `Settings.llm` / embed model
- README mentions `OPENAI_API_KEY` but `app.py` does not wire it

See [archive README](../README.md).
