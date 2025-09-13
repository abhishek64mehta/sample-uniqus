# agent.py
import re
import json
from collections import defaultdict

class Agent:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline

    def handle_query(self, query):
        # Very simple dispatcher: if comparative keywords present, decompose
        if self._is_comparative(query):
            sub_queries = self._decompose(query)
            gathered = []
            for sq in sub_queries:
                res = self.rag.retrieve(sq, top_k=3)
                gathered.append({'sub_query': sq, 'results': res})
            answer, reasoning = self._synthesize_comparative(query, gathered)
            return {
                'query': query,
                'answer': answer,
                'reasoning': reasoning,
                'sub_queries': [g['sub_query'] for g in gathered],
                'sources': self._format_sources(gathered)
            }
        else:
            res = self.rag.retrieve(query, top_k=5)
            answer = self._synthesize_simple(query, res)
            return {
                'query': query,
                'answer': answer,
                'reasoning': 'Retrieved top chunks and synthesized.',
                'sub_queries': [query],
                'sources': self._format_sources([{'sub_query': query, 'results': res}])
            }

    def _is_comparative(self, q):
        keywords = ['compare', 'how did', 'growth', 'which of', 'which company', 'change from']
        ql = q.lower()
        return any(k in ql for k in keywords)

    def _decompose(self, q):
        # naive decomposition: find companies & years & metrics
        companies = ['Microsoft', 'Google', 'NVIDIA', 'NVIDA', 'GOOGL', 'MSFT', 'NVDA']
        years = re.findall(r'20\d{2}', q)
        metrics = []
        # try to extract metric words
        metric_patterns = ['revenue', 'operating margin', 'gross margin', 'cloud revenue', 'data center revenue', 'R&D', 'research and development', 'percentage of revenue']
        for m in metric_patterns:
            if m in q.lower():
                metrics.append(m)
        # build sub-queries
        sub_queries = []
        if 'compare' in q.lower() or 'which' in q.lower():
            # compare across companies
            for c in ['Microsoft', 'Google', 'NVIDIA']:
                for y in years or ['2023']:
                    metric = metrics[0] if metrics else 'operating margin'
                    sub_queries.append(f"{c} {metric} {y}")
        else:
            # fallback: simple year based decomposition
            if years and metrics:
                for y in years:
                    sub_queries.append(f"{metrics[0]} {y}")
        return sub_queries

    def _synthesize_comparative(self, query, gathered):
        # Very simple synthesis: for each sub_query take the first source meta and summarize
        rows = []
        for g in gathered:
            sq = g['sub_query']
            if g['results']:
                meta = g['results'][0]['meta']
                excerpt = (meta.get('excerpt') if 'excerpt' in meta else '') or f"(from {meta.get('file')})"
                rows.append((sq, excerpt))
            else:
                rows.append((sq, 'NOT FOUND'))
        answer = ' | '.join([f"{r[0]} => {r[1]}" for r in rows])
        reasoning = 'Executed sub-queries and compared retrieved values.'
        return answer, reasoning

    def _synthesize_simple(self, query, res):
        if not res:
            return 'No relevant information found.'
        meta = res[0]['meta']
        return f"Found relevant excerpt in {meta.get('file')} (company={meta.get('company')}, year={meta.get('year')})"

    def _format_sources(self, gathered):
        sources = []
        for g in gathered:
            for r in g['results']:
                m = r['meta']
                sources.append({'company': m.get('company'), 'year': m.get('year'), 'file': m.get('file')})
        return sources
