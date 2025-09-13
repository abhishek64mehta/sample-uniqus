# utils/helpers.py
import re


def chunk_text(text, min_tokens=200, max_tokens=600):
    # naive chunker based on sentences; tokens approximated by words
    sentences = re.split(r'(?<=[\.!?])\s+', text)
    chunks = []
    cur = []
    cur_len = 0
    for s in sentences:
        wcount = len(s.split())
        if cur_len + wcount > max_tokens and cur:
            chunks.append(' '.join(cur))
            cur = [s]
            cur_len = wcount
        else:
            cur.append(s)
            cur_len += wcount
    if cur:
        chunks.append(' '.join(cur))
    # ensure min_tokens by merging small chunks
    merged = []
    i = 0
    while i < len(chunks):
        if len(merged) == 0 or len(merged[-1].split()) >= min_tokens:
            merged.append(chunks[i])
        else:
            merged[-1] = merged[-1] + ' ' + chunks[i]
        i += 1
    return merged
