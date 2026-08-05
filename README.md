# Mutual Fund FAQ Assistant

A facts-only Retrieval-Augmented Generation (RAG) assistant designed to answer verifiable queries about specific mutual fund schemes. Built with FastAPI, Next.js, ChromaDB, and Groq's Llama 3 API.

## Selected Schemes
This assistant uses information strictly scraped from the following Groww scheme pages:
1. [HDFC Mid-Cap Opportunities Fund](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
2. [HDFC Small Cap Fund](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)
3. [ICICI Prudential Technology Fund](https://groww.in/mutual-funds/icici-prudential-technology-fund-direct-growth)
4. [Nippon India Small Cap Fund](https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth)
5. [Axis Small Cap Fund](https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth)

## Architecture Overview
The system consists of two pipelines:
1. **Offline Pipeline (Data Ingestion):** Scrapes the specific Groww URLs, cleans the HTML, chunks the text, and generates embeddings using `BAAI/bge-small-en-v1.5`. These embeddings are stored locally in a ChromaDB vector store.
2. **Online Pipeline (Chat):** 
   - A user submits a query through the **Next.js** frontend.
   - The **FastAPI** backend receives it and runs it through a classifier. 
   - If the query asks for advice (e.g., "Should I invest?") or contains PII (e.g., PAN numbers), it is instantly blocked.
   - If factual, the query is embedded and similar chunks are retrieved from ChromaDB.
   - The chunks and user query are sent to **Groq (Llama 3)** to generate a response (≤ 3 sentences).
   - The response is post-processed to inject a source URL and a "Last updated from sources" date footer.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js & npm
- A Groq API key

### 1. Environment Setup
Create a `.env` file in the root directory and add your API key:
```env
GROQ_API_KEY=your_api_key_here
```

### 2. Backend Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Build the vector database (scrape and index):
   ```bash
   python src/scraper.py
   python src/parser.py
   python src/embedder.py
   ```
3. Run the FastAPI backend:
   ```bash
   cd src
   python main.py
   ```
   The backend will be available at `http://localhost:8000`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies and start the development server:
   ```bash
   npm install
   npm run dev
   ```
3. Open `http://localhost:3000` in your browser.

## Automated Data Refresh (GitHub Actions)

The knowledge base is automatically refreshed via a **GitHub Actions** cron workflow.

### How It Works
The workflow at [`.github/workflows/scheduler.yml`](.github/workflows/scheduler.yml) runs the data-ingestion pipeline (`scraper → parser → embedder`) on a daily schedule. It can also be triggered manually from the GitHub **Actions** tab.

| Setting | Value |
|---------|-------|
| Schedule | Every day at **10:30 AM IST** (05:00 UTC) |
| Cron expression | `0 5 * * *` |
| Workflow file | `.github/workflows/scheduler.yml` |
| Orchestration script | `src/scheduler.py` |

### Changing the Schedule
Edit the `cron` field in `.github/workflows/scheduler.yml`:
```yaml
on:
  schedule:
    - cron: "0 5 * * *"   # ← change this (minute hour day month weekday, UTC)
```
Useful examples:
- `"0 6 * * *"` → every day at 06:00 UTC
- `"0 0 * * 1"` → every Monday at midnight UTC
- `"0 */6 * * *"` → every 6 hours

### Required GitHub Secret
The workflow needs the Groq API key. Add it once via **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|-------------|-------|
| `GROQ_API_KEY` | Your Groq API key |

### Running Manually
You can also run the pipeline locally at any time:
```bash
python src/scheduler.py
```

## Known Limitations
- **Daily Corpus Refresh**: Data is refreshed once daily via GitHub Actions. Changes to the source pages between runs will not be reflected until the next scheduled run.
- **Limited Scope**: The assistant only knows about the 5 explicitly scraped funds and only knows the data available on their specific Groww pages.
- **No Conversation Memory**: The assistant treats each query independently and cannot remember previous messages in the chat session.
- **External Dependency**: Responses require a connection to the Groq API for LLM generation.

