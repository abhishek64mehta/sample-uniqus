# RAG Sprint Challenge — Financial Q&A System


## Overview
This repo provides a focused Retrieval-Augmented Generation (RAG) system with simple agent capabilities for decomposing comparative queries and synthesizing answers from SEC 10-K filings (Google, Microsoft, NVIDIA; years 2022--2024).


> NOTE: This implementation is intentionally lightweight and designed to run locally. It uses sentence-transformers for embeddings and FAISS for vector search. Agent decomposition is rule-based (simple pattern matching) to avoid dependence on an LLM for control flow. You may optionally wire an LLM (OpenAI/Gemini) for improved synthesis.


## Files
- `main.py` — entrypoint: builds index (or uses cached), runs queries and demonstrates sample outputs.
- `rag_pipeline.py` — ingestion, chunking, embeddings, vector store, retrieval.
- `agent.py` — simple agent that decides decomposition for comparative queries and orchestrates retrieval + synthesis.
- `utils/sec_downloader.py` — helper to download 10-Ks from EDGAR (scraper). Optional; you can also place downloaded files under `data/`.
- `utils/text_extract.py` — extracts text from PDF/HTML using `pdfplumber` and BeautifulSoup.
- `utils/helpers.py` — shared helper functions.
- `sample_outputs.json` — example outputs for the 5 required query types (provided as examples; your run will output actual JSON responses once filings are ingested).
- `design_doc.md` — one-page design doc describing chunking choice, embedding model, agent approach.


## Quick setup


1. Create and activate a Python 3.10+ virtual environment


```bash
python -m venv venv
source venv/bin/activate # macOS / Linux
venv\Scripts\activate # Windows
