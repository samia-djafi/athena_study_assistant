"""
Athena AI/CS Study Assistant — FastAPI Application Entry Point.
"""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.db import init_db
from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.api.documents import router as documents_router
from app.api.quiz import router as quiz_router
from app.api.learning import router as learning_router
from app.api.health import router as health_router

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("athena")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    logger.info("Initializing Athena backend & SQLite/Supabase storage layer...")
    await init_db()
    logger.info("Athena backend initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down Athena backend.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent, adaptive, multi-agent educational assistant for Computer Science & AI learners.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"{request.method} {request.url.path} - Error: {exc} ({process_time:.2f}ms)")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred.", "error": str(exc)}
        )

# Register API v1 Routers
API_V1_PREFIX = "/api/v1"
app.include_router(chat_router, prefix=API_V1_PREFIX)
app.include_router(sessions_router, prefix=API_V1_PREFIX)
app.include_router(documents_router, prefix=API_V1_PREFIX)
app.include_router(quiz_router, prefix=API_V1_PREFIX)
app.include_router(learning_router, prefix=API_V1_PREFIX)
app.include_router(health_router, prefix=API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs"
    }
