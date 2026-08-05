# Constants and configurations

# Target URLs to scrape for Mutual Fund information
URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/icici-prudential-technology-fund-direct-growth",
    "https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth"
]

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K = 3 # 3 to 5 chunks

# LLM settings
TEMPERATURE = 0.1
MAX_TOKENS = 150

# Groq rate limits for llama-3.3-70b-versatile
GROQ_REQUESTS_PER_MINUTE = 30
GROQ_REQUESTS_PER_DAY = 1000
GROQ_TOKENS_PER_MINUTE = 12000
GROQ_TOKENS_PER_DAY = 100000
