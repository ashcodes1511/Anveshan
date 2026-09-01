from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routes import events

app = FastAPI(
    title="Anveshan API",
    description="Real-time risk-scoring engine for SIM-swap and account-takeover fraud detection.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api", tags=["events"])


@app.get("/")
def dashboard():
    return FileResponse("../frontend/dashboard.html")


@app.get("/health")
def health():
    return {"status": "ok"}