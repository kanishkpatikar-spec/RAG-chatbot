import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from classifier import classify_query
from retriever import retrieve
from generator import generate
from formatter import format_response

app = FastAPI(title="Mutual Fund Assistant API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    prompt = request.query
    
    # Step 1: Classification & Guardrails
    classification = classify_query(prompt)
    if not classification.is_allowed:
        return ChatResponse(response=classification.refusal_message)
        
    # Step 2: Retrieval
    retrieval = retrieve(prompt)
    
    # Step 3: Generation
    generation = generate(
        context=retrieval.context,
        user_query=prompt,
        source_urls=retrieval.source_urls,
        scraped_dates=retrieval.scraped_dates,
    )
    
    # Step 4: Formatting
    if generation.success:
        final_response = format_response(
            raw_response=generation.response,
            source_urls=generation.source_urls,
            scraped_dates=generation.scraped_dates
        )
    else:
        final_response = generation.error_message or "An error occurred during generation."
        
    return ChatResponse(response=final_response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
