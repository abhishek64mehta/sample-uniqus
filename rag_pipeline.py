# rag_pipeline.py
import os
import glob
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from utils.text_extract import extract_text_from_file
from utils.helpers import chunk_text


class RAGPipeline:
    def __init__(self, data_dir='data', index_dir='index', model_name='all-MiniLM-L6-v2'):
        self.data_dir = data_dir
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []  # list of dict {company, year, file, chunk_id, text}

    def index_exists(self):
        return os.path.exists(os.path.join(self.index_dir, 'faiss.index'))

    def download_filings(self):
        # Lightweight wrapper that calls util downloader (fetches PDFs/HTMLs into data_dir)
        from utils.sec_downloader import download_10k_filings_for_companies
        companies = {
            'GOOGL': '1652044',
            'MSFT': '789019',
            'NVDA': '1045810'
        }
        years = [2022, 2023, 2024]
        download_10k_filings_for_companies(companies, years, out_dir=self.data_dir)

    def build(self):
        files = glob.glob(os.path.join(self.data_dir, '**', '*.*'), recursive=True)
        print(f'Found {len(files)} files for ingestion')
        all_text_chunks = []
        self.metadata = []
        for fpath in files:
            try:
                text = extract_text_from_file(fpath)
            except Exception as e:
                print('Failed to extract', fpath, e)
                continue
            chunks = chunk_text(text, min_tokens=200, max_tokens=600)
            base = os.path.basename(fpath)
            # Try to infer company/year from path
            parts = fpath.split(os.sep)
            company = parts[-2] if len(parts) >= 2 else 'UNKNOWN'
            year = 'UNKNOWN'
            for p in parts:
                if p.isdigit() and len(p) == 4:
                    year = p
            for i, c in enumerate(chunks):
                meta = {'file': base, 'path': fpath, 'company': company, 'year': year, 'chunk_id': len(self.metadata)}
                self.metadata.append(meta)
                all_text_chunks.append(c)
        print('Total chunks:', len(all_text_chunks))
        if not all_text_chunks:
            raise RuntimeError('No text chunks to index. Place files under data/ or run downloader.')
        embeddings = self.model.encode(all_text_chunks, show_progress_bar=True, convert_to_numpy=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        faiss.write_index(index, os.path.join(self.index_dir, 'faiss.index'))
        with open(os.path.join(self.index_dir, 'metadata.json'), 'w') as f:
            json.dump(self.metadata, f)
        self.index = index
        print('Index built and saved')

    def load_index(self):
        import json
        self.index = faiss.read_index(os.path.join(self.index_dir, 'faiss.index'))
        with open(os.path.join(self.index_dir, 'metadata.json'), 'r') as f:
            self.metadata = json.load(f)
        self.model = SentenceTransformer(self.model._config_name)
        print('Index and metadata loaded')

    def retrieve(self, query, top_k=5):
        emb = self.model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(emb, top_k)
        results = []
        for iid in I[0]:
            meta = self.metadata[int(iid)]
            results.append({'meta': meta})
        return results
