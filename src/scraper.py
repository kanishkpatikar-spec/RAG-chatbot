import os
import sys
import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Add the project root to the python path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import URLS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_slug_from_url(url):
    """Extracts the slug from the Groww mutual fund URL."""
    return url.strip("/").split("/")[-1]

def scrape_and_save(page, url, output_dir="data/raw"):
    """
    Fetches the HTML content of a given URL using Playwright and saves it.
    """
    slug = get_slug_from_url(url)
    filepath = os.path.join(output_dir, f"{slug}.html")
    
    try:
        logging.info(f"Fetching URL with Playwright: {url}")
        # Wait until network is mostly idle to ensure JS has loaded data
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        html_content = page.content()
        
        # Simple verification using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string if soup.title else "No Title Found"
        logging.info(f"Page Title: {title}")
        
        # Save raw HTML
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logging.info(f"Successfully saved rendered HTML to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return False

def main():
    logging.info("Starting Phase 1A: Web Scraper (Playwright)")
    
    # Ensure output directory exists relative to project root
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    
    success_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for url in URLS:
            if scrape_and_save(page, url, output_dir):
                success_count += 1
                
        browser.close()
            
    logging.info(f"Scraper finished. Successfully scraped {success_count}/{len(URLS)} URLs.")

if __name__ == "__main__":
    main()

