"""
Multi-Tenant Schema Translator - Main Application
AI-powered contract data querying across diverse customer schemas

REFACTORED VERSION - Demonstrates:
- Separation of concerns
- Dependency injection
- Error resilience
- Clean architecture
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import queries, mappings

# Initialize settings and logging
settings = get_settings()
setup_logging(level="INFO" if not settings.DEBUG else "DEBUG")
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Multi-Tenant Schema Translator",
    version="2.0.0",
    description="AI-powered multi-tenant contract query system with semantic understanding"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI (before routes to avoid conflicts)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info("Static files mounted at /static")
    
    # Serve index.html at root
    @app.get("/", response_class=FileResponse)
    async def read_root():
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return index_path
        return {"message": "Multi-Tenant Schema Translator API", "version": "2.0.0"}

# Register routes (essential for UI demo)
app.include_router(queries.router)    # Natural language queries
app.include_router(mappings.router)   # Schema mapping generation

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for testing"""
    return {"status": "healthy", "version": "2.0.0"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info("=" * 60)
    logger.info("Multi-Tenant Schema Translator API Starting")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("Multi-Tenant Schema Translator API Shutting Down")


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
