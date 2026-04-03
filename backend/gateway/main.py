"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from backend.api import health, auth
from backend.gateway import routes as inference
from backend.gateway.config import settings
from backend.utils.logging import setup_logging, get_logger
from backend.utils.exceptions import SecurityBlockError
import os

# Setup logging
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Debug Mode: {settings.debug}")
    yield
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## RectitudeAI - LLM Security Gateway

    Multi-layer defense system for LLM applications.

    ### Current Features (Phase 1 & Phase 2)
    - ✅ JWT Authentication
    - ✅ Rate Limiting
    - ✅ Structured Logging
    - ✅ LLM Integration (OpenAI/Anthropic/Ollama)
    - ✅ Prompt Injection Detection (distilbert)
    - ✅ Harmful Intent Detection (toxic-bert)
    - ✅ Perplexity-based Obfuscation Detection (gpt2)
    - ✅ Risk Fusion Policy Engine

    ### Coming Soon (Phase 3-5)
    - 🔜 Cryptographic Tool Signing
    - 🔜 Red Team Engine
    - 🔜 Behavioral Anomaly Detection

    ### Team
    - **Ayush Tandon** - Backend & ML
    - **Vartika Manish** - Security & Cryptography
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register exception handler for blocked prompts
@app.exception_handler(SecurityBlockError)
async def security_block_exception_handler(request: Request, exc: SecurityBlockError):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc.args[0]),
            "risk_score": exc.args[1],
            "metadata": exc.args[2],
        },
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(inference.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.gateway.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )