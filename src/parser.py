import os
import sys
import glob
import json
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Add the project root to the python path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import URLS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_html(html_content):
    """
    Parses HTML, removes unwanted sections, and returns structured text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg']):
        tag.decompose()
        
    # Remove elements by common class names that indicate noise
    for tag in soup.find_all(class_=re.compile(r'header|footer|nav|menu|sidebar|breadcrumb', re.I)):
        tag.decompose()
        
    # Get all text with double newline to separate block elements nicely
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up multiple newlines (reduce 3+ newlines to 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text, soup

def extract_metadata(soup, filename):
    """
    Extracts metadata from the parsed HTML and filename.
    """
    # Scheme Name from title
    title = soup.title.string if soup.title else ""
    scheme_name = title.split('-')[0].strip() if '-' in title else title.strip()
    
    # Source URL inferred from filename
    slug = filename.replace('.html', '')
    source_url = f"https://groww.in/mutual-funds/{slug}"
    
    # Attempt to extract category
    category = "Mutual Fund" # Default
    text = soup.get_text(separator=' ', strip=True)
    match = re.search(r'Category average\s*\(\s*(.*?)\s*\)', text)
    if match:
        category = match.group(1).strip()
        
    return {
        "scheme_name": scheme_name,
        "source_url": source_url,
        "category": category,
        "scraped_date": datetime.now().isoformat()
    }

def chunk_documents():
    """
    Reads processed text files, applies chunking, and returns chunks with metadata.
    Uses chunk size of 2000 chars (~500 tokens) and overlap of 200 chars (~50 tokens).
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    txt_files = glob.glob(os.path.join(processed_dir, "*.txt"))
    if not txt_files:
        logging.warning("No processed .txt files found. Run Phase 1B first.")
        return []
        
    # Using characters as approximation: 1 token ~ 4 characters
    # 500 tokens -> 2000 chars, 50 tokens -> 200 chars
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    all_chunks = []
    
    for txt_path in txt_files:
        slug = os.path.basename(txt_path).replace('.txt', '')
        json_path = os.path.join(processed_dir, f"{slug}.json")
        
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # Create LangChain Document
            doc = Document(page_content=text, metadata=metadata)
            
            # Split into chunks
            doc_chunks = splitter.split_documents([doc])
            
            # Attach chunk_index to metadata
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata['chunk_index'] = i
                all_chunks.append(chunk)
                
            logging.info(f"Chunked {slug} into {len(doc_chunks)} chunks.")
        except Exception as e:
            logging.error(f"Error chunking {slug}: {e}")
            
    return all_chunks

def main():
    logging.info("Starting Phase 1B: Document Parser & Cleaner")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    os.makedirs(processed_dir, exist_ok=True)
    
    html_files = glob.glob(os.path.join(raw_dir, "*.html"))
    
    if not html_files:
        logging.warning(f"No HTML files found in {raw_dir}. Run Phase 1A first.")
        return
        
    success_count = 0
    for filepath in html_files:
        filename = os.path.basename(filepath)
        slug = filename.replace('.html', '')
        
        logging.info(f"Processing {filename}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            text_content, soup = clean_html(html_content)
            metadata = extract_metadata(soup, filename)
            
            # Save .txt
            txt_path = os.path.join(processed_dir, f"{slug}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
                
            # Save .json
            json_path = os.path.join(processed_dir, f"{slug}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
                
            success_count += 1
            logging.info(f"Successfully processed and saved {slug}")
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            
    logging.info(f"Parser finished. Successfully processed {success_count}/{len(html_files)} files.")

if __name__ == "__main__":
    main()
