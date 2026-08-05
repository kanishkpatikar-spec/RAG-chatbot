"""Quick script to understand chunks and embeddings in depth."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import chromadb

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
persist_dir = os.path.join(base_dir, "vectorstore")

client = chromadb.PersistentClient(path=persist_dir)
collection = client.get_collection(name="mutual_fund_faq")

# Get ALL documents with metadata
results = collection.get(include=["documents", "metadatas"])

docs = results["documents"]
metas = results["metadatas"]

print(f"Total chunks: {len(docs)}")
print()

# Distribution by scheme
from collections import Counter
scheme_counts = Counter(m.get("scheme_name", "Unknown") for m in metas)
print("=== Chunks per Scheme ===")
for scheme, count in scheme_counts.most_common():
    print(f"  {scheme}: {count} chunks")
print()

# Show content length stats
lengths = [len(d) for d in docs]
print(f"=== Chunk Length Stats (chars) ===")
print(f"  Min: {min(lengths)}")
print(f"  Max: {max(lengths)}")
print(f"  Avg: {sum(lengths)/len(lengths):.0f}")
print()

# Show metadata keys available
print(f"=== Metadata Keys ===")
print(f"  {list(metas[0].keys())}")
print()

# Show a few representative chunks with their content
print("=== Sample Chunks (first 300 chars each) ===")
for i in [0, 5, 10, 20, 30]:
    if i < len(docs):
        print(f"\n--- Chunk {i} (scheme: {metas[i].get('scheme_name')}, chunk_idx: {metas[i].get('chunk_index')}) ---")
        snippet = docs[i][:300].replace('\n', ' | ')
        print(f"  {snippet}...")

# Test retrieval with a realistic query
print("\n\n=== Test Retrieval: 'expense ratio HDFC Mid-Cap' ===")
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

vectorstore = Chroma(
    persist_directory=persist_dir,
    embedding_function=embeddings,
    collection_name="mutual_fund_faq"
)

# Test several queries
queries = [
    "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?",
    "What is the minimum SIP amount?",
    "exit load HDFC Small Cap",
    "fund manager Nippon India Small Cap",
]

for q in queries:
    print(f"\nQuery: {q}")
    results = vectorstore.similarity_search_with_relevance_scores(q, k=3)
    for i, (doc, score) in enumerate(results):
        print(f"  [{i+1}] Score: {score:.4f} | Scheme: {doc.metadata.get('scheme_name')} | Chunk: {doc.metadata.get('chunk_index')} | Content: {doc.page_content[:120].replace(chr(10), ' ')}...")
