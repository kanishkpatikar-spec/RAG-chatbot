import os
import sys
import logging
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from parser import chunk_documents

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_vector_store():
    """
    Phase 2.3 & 2.4: Generates embeddings using BAAI/bge-small-en-v1.5 and stores them in ChromaDB.
    """
    logging.info("Starting Phase 2: Generating Embeddings & Storing in ChromaDB")
    
    # 1. Get chunked documents from Phase 2.1 & 2.2
    chunks = chunk_documents()
    if not chunks:
        logging.error("No chunks returned from parser. Exiting.")
        return None
        
    logging.info(f"Loaded {len(chunks)} chunks for embedding.")
    
    # 2. Initialize the BGE embedding model (Phase 2.3)
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'} # Change to 'cuda' if GPU is available
    encode_kwargs = {'normalize_embeddings': True} # BGE models recommend normalized embeddings
    
    logging.info(f"Loading embedding model: {model_name}...")
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    # 3. Store in ChromaDB (Phase 2.4)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persist_directory = os.path.join(base_dir, "vectorstore")
    
    logging.info(f"Storing embeddings in ChromaDB at: {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="mutual_fund_faq"
    )
    
    # Ensure it persists
    vectorstore.persist()
    logging.info("ChromaDB vector store created and persisted successfully.")
    
    return vectorstore

def verify_index(vectorstore):
    """
    Phase 2.5: Run a sample query to confirm retrieval works.
    """
    test_query = "expense ratio HDFC Mid-Cap"
    logging.info(f"Verifying index with test query: '{test_query}'")
    
    results = vectorstore.similarity_search(test_query, k=3)
    
    if results:
        logging.info("Verification successful. Top 3 relevant chunks retrieved:")
        for i, res in enumerate(results):
            logging.info(f"Result {i+1}: (Scheme: {res.metadata.get('scheme_name')}) -> {res.page_content[:100].replace('\n', ' ')}...")
    else:
        logging.warning("Verification failed. No results found.")

def main():
    vectorstore = create_vector_store()
    if vectorstore:
        verify_index(vectorstore)

if __name__ == "__main__":
    main()
