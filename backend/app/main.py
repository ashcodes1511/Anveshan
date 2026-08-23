"""
Anveshan - Real-Time SIM-Swap & Account-Takeover Fraud Detection
Entry point for the FastAPI backend.

Run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import events

app = FastAPI(
    title="Anveshan API",
    description="Real-time risk-scoring engine for SIM-swap and account-takeover fraud detection.",
    version="0.1.0",
)

# Allow the (future) React dashboard to call this API during local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api", tags=["events"])


@app.get("/")
def root():
    return {
        "service": "Anveshan API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
