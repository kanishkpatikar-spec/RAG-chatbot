import os
import sys
import logging
import requests
from bs4 import BeautifulSoup

# Add the project root to the python path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import URLS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_slug_from_url(url):
    """Extracts the slug from the Groww mutual fund URL."""
    return url.strip("/").split("/")[-1]

def scrape_and_save(url, output_dir="data/raw"):
    """
    Fetches the HTML content of a given URL and saves it to the output directory.
    Note: Phase 1A ensures we fetch the raw HTML. Extraction of meaningful sections 
    (scheme name, expense ratio, exit load, etc.) will be handled in Phase 1B (parser.py) 
    using the saved raw HTML.
    """
    slug = get_slug_from_url(url)
    filepath = os.path.join(output_dir, f"{slug}.html")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logging.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        html_content = response.text
        
        # Simple verification using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string if soup.title else "No Title Found"
        logging.info(f"Page Title: {title}")
        
        # Save raw HTML
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logging.info(f"Successfully saved raw HTML to {filepath}")
        return True
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return False

def main():
    logging.info("Starting Phase 1A: Web Scraper")
    
    # Ensure output directory exists relative to project root
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    
    success_count = 0
    for url in URLS:
        if scrape_and_save(url, output_dir):
            success_count += 1
            
    logging.info(f"Scraper finished. Successfully scraped {success_count}/{len(URLS)} URLs.")

if __name__ == "__main__":
    main()
