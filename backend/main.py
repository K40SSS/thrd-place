"""
Main FastAPI application entry point.
Initializes the FastAPI server and includes all routes.
Configured for CORS to allow frontend communication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import route routers
from routes.auth_route import router as auth_router
from routes.sessions import router as sessions_router
from routes.chat_route import router as chat_router
from config import settings

# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for StudyMate - A study session coordination platform",
    docs_url="/api/docs",  # Swagger UI documentation
    redoc_url="/api/redoc"  # ReDoc documentation
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend to make requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
# Auth routes: /auth/*
app.include_router(auth_router)

# Session routes: /sessions/*
app.include_router(sessions_router)

# Chat routes: /chat/*
app.include_router(chat_router)


# ==================== ROOT ROUTES ====================

@app.get("/", tags=["General"])
def root():
    """
    Root endpoint - API welcome message.
    Use this to verify the backend is running.
    """
    return {
        "message": "Welcome to StudyMate API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health"
    }


@app.get("/health", tags=["General"])
def health_check():
    """
    Health check endpoint for deployment monitoring.
    Returns the status of the application.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Handle 404 Not Found errors with a custom response.
    """
    return {
        "error": "Not Found",
        "detail": "The requested endpoint does not exist",
        "path": request.url.path
    }


# ==================== STARTUP AND SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """
    Called when the application starts.
    Use for initialization tasks (e.g., database connections).
    """
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Debug mode: {settings.DEBUG}")
    print("Backend is ready to handle requests!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Called when the application shuts down.
    Use for cleanup tasks.
    """
    print("Shutting down backend...")


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    # In production, use a proper ASGI server like Gunicorn with Uvicorn workers
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )