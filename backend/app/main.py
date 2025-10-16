"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🏀 Fantasy Basketball Oracle v{settings.VERSION} starting up...")
    print(f"📊 League: {settings.LEAGUE_SIZE} teams, 9-cat scoring")
    
    yield
    
    # Shutdown
    print("Shutting down Fantasy Basketball Oracle...")


app = FastAPI(
    title="Fantasy Basketball Oracle",
    description="Your intelligent fantasy basketball assistant",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fantasy Basketball Oracle API",
        "version": settings.VERSION,
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": settings.VERSION
        }
    )
