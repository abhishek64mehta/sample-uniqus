# utils/text_extract.py
import pdfplumber
from bs4 import BeautifulSoup


def extract_text_from_file(path):
    if path.lower().endswith('.pdf'):
        with pdfplumber.open(path) as pdf:
            texts = [p.extract_text() or '' for p in pdf.pages]
        return '\n'.join(texts)
    else:
        # treat as HTML/text
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n')
