# Archived — multimodal-rag

**Status:** Not maintained. Preserved as a multimodal RAG experiment (Streamlit + FastAPI + Chroma + CLIP).

**Known gaps when archived:**

- No `requirements.txt` at project root
- README says `streamlit run src/ui.py` — actual UI is `app.py`
- `src/api/data_loader.py` only ingests images; PDF/TXT/DOCX paths are commented out
- Expects LM Studio at `http://localhost:1234/v1` and `TOGETHER_API_KEY` for captions
- `langchain.text_splitter` import may fail on LangChain ≥ 0.2

See [archive README](../README.md).
