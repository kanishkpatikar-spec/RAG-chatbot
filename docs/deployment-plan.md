# Deployment Plan: RAG Chatbot

This document outlines the step-by-step deployment process for the Mutual Fund Assistant (RAG Chatbot) with the backend on Railway and the frontend on Vercel.

## 1. Prerequisites
- GitHub account with the repository pushed.
- Railway account linked to GitHub.
- Vercel account linked to GitHub.

## 2. Backend Deployment (Railway)

The backend is a FastAPI application. Railway will use the `railway.toml` file at the root of the repository to configure the deployment.

### Setup Steps:
1. **Login to Railway** and click **New Project**.
2. Select **Deploy from GitHub repo** and choose your `RAG-chatbot` repository.
3. **Configure the Service**:
   - Railway automatically detects the `railway.toml` file in the root directory.
   - The start command is already configured to run the uvicorn server on the dynamic `$PORT`.
4. **Environment Variables**:
   - On the Railway project canvas, **click on the block representing your GitHub repository** (the service) to open its settings panel.
   - In the panel that opens, click on the **Variables** tab.
   - Click **New Variable** (or click inside the empty input box).
   - Enter `GROQ_API_KEY` as the **VARIABLE_NAME** and your actual key (e.g., `gsk_...`) as the **VALUE**.
   - Click **Add** (or press Enter).
5. **Generate Public URL**:
   - Go to the **Settings** tab.
   - Under **Networking** or **Environment**, click **Generate Domain** (or attach a custom domain).
   - *Note the generated URL (e.g., `https://your-backend-app.up.railway.app`). You will need this for the frontend.*
6. **Deploy**:
   - Railway will automatically build and deploy. Wait for the status to show a green success indicator.

> [!WARNING]  
> Railway provides ephemeral filesystems by default. The `vectorstore` folder (containing the ChromaDB data) must be committed to your repository so it's available at runtime. If you plan to update embeddings dynamically via a scheduler in the cloud, you'll need to configure a **Persistent Volume** in Railway and update the path in your code.

## 3. Frontend Deployment (Vercel)

The frontend is a Next.js application located in the `frontend` subdirectory.

### Setup Steps:
1. **Login to Vercel** and click **Add New... > Project**.
2. **Import Git Repository**: Select the `RAG-chatbot` repository.
3. **Configure Project**:
   - **Root Directory**: Click "Edit" and select `frontend`.
   - **Framework Preset**: Vercel should automatically detect **Next.js**.
   - **Build and Output Settings**: Leave as default.
4. **Environment Variables**:
   - You need to add an environment variable to tell the frontend where the Railway backend is located.
   - **Variable Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: The Railway public URL generated in Step 2.5 (e.g., `https://your-backend-app.up.railway.app`).
5. **Deploy**:
   - Click **Deploy**. Vercel will build and assign a public URL for your frontend application.

## 4. Code Modifications Needed Before Deployment

Before deploying, ensure these minor adjustments are made so both services can communicate.

### Update Frontend API Call
The frontend currently hardcodes `http://localhost:8000`. Update it to use the environment variable.

In `frontend/src/app/page.tsx` (around line 119):
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const response = await fetch(`${apiUrl}/api/chat`, {
    // ...
```

### Update Backend CORS Options
The backend must accept requests from the Vercel domain.

In `src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    # Add your Vercel URL to allow_origins once it is generated, or use ["*"]
    allow_origins=["http://localhost:3000", "https://your-vercel-domain.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 5. Verification
1. Once both deployments are live, navigate to your Vercel frontend URL.
2. Ask a factual question (e.g., *"What is the expense ratio of HDFC Mid-Cap Opportunities Fund?"*).
3. If you receive a correct, formatted response, your Next.js frontend has successfully communicated with the FastAPI backend on Railway.
