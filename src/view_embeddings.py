import os
import chromadb
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def view_embeddings():
    """
    Connects to the local ChromaDB and prints a sample of chunks along with 
    a summary of their embedding vectors.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persist_directory = os.path.join(base_dir, "vectorstore")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Get our specific collection
    collection_name = "mutual_fund_faq"
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        logging.error(f"Failed to get collection '{collection_name}': {e}")
        return
        
    # Total count
    total_docs = collection.count()
    logging.info(f"Total chunks in '{collection_name}' collection: {total_docs}\n")
    
    if total_docs == 0:
        logging.info("No chunks to display.")
        return

    # Fetch a few samples (including embeddings)
    # We specify include=['embeddings', 'documents', 'metadatas'] to ensure embeddings are returned
    sample_size = min(3, total_docs)
    results = collection.get(
        limit=sample_size,
        include=['embeddings', 'documents', 'metadatas']
    )
    
    embeddings = results.get('embeddings', [])
    documents = results.get('documents', [])
    metadatas = results.get('metadatas', [])
    
    for i in range(sample_size):
        logging.info(f"--- Chunk {i+1} ---")
        logging.info(f"Scheme Name: {metadatas[i].get('scheme_name')}")
        
        # Print a snippet of the text
        doc_snippet = documents[i].replace('\n', ' ')
        if len(doc_snippet) > 100:
            doc_snippet = doc_snippet[:100] + "..."
        logging.info(f"Text Snippet: {doc_snippet}")
        
        # Print embedding details
        emb = embeddings[i]
        logging.info(f"Embedding Length (Dimensions): {len(emb)}")
        
        # Print the first 5 and last 5 values of the embedding vector to give an idea of what it looks like
        emb_preview = f"[{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ..., {emb[-2]:.4f}, {emb[-1]:.4f}]"
        logging.info(f"Embedding Vector Preview: {emb_preview}\n")

if __name__ == "__main__":
    view_embeddings()
