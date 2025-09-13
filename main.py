# main.py
import argparse
import json
import os
from rag_pipeline import RAGPipeline
from agent import Agent


DATA_DIR = "data"
INDEX_DIR = "index"
SAMPLE_OUTPUTS = "sample_outputs.json"


SAMPLE_QUERIES = [
# Simple queries
"What was NVIDIA's total revenue in fiscal year 2024?",
"What percentage of Google's 2023 revenue came from advertising?",
# Comparative queries (require agent decomposition)
"How much did Microsoft's cloud revenue grow from 2022 to 2023?",
"Which of the three companies had the highest gross margin in 2023?",
# Complex multi-step queries
"Compare the R&D spending as a percentage of revenue across all three companies in 2023",
"How did each company's operating margin change from 2022 to 2024?",
"What are the main AI risks mentioned by each company and how do they differ?"
]




def main(download=False, rebuild=False):
os.makedirs(DATA_DIR, exist_ok=True)
pipeline = RAGPipeline(data_dir=DATA_DIR, index_dir=INDEX_DIR)


if download:
print("Running SEC downloader (this may take time)...")
pipeline.download_filings() # uses utils/sec_downloader


if rebuild or not pipeline.index_exists():
print("Building index...")
pipeline.build()
else:
pipeline.load_index()


agent = Agent(pipeline)


outputs = []
for q in SAMPLE_QUERIES:
print("\nQUERY:\n", q)
resp = agent.handle_query(q)
print(json.dumps(resp, indent=2))
outputs.append(resp)


with open(SAMPLE_OUTPUTS, "w") as f:
json.dump(outputs, f, indent=2)
print("Sample outputs written to", SAMPLE_OUTPUTS)




if __name__ == '__main__':
parser = argparse.ArgumentParser()
parser.add_argument('--download', action='store_true')
parser.add_argument('--rebuild', action='store_true')
args = parser.parse_args()
main(download=args.download, rebuild=args.rebuild)
