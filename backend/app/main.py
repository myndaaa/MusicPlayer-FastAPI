# Entry point for the FastAPI application
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.custom_exception import PasswordVerificationError, JWTExpiredError, JWTDecodeError
from app.core.exception_handler import (
    password_verification_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    jwt_expired_exception_handler,
    jwt_decode_exception_handler
)

# Import database models to ensure they are loaded
from app.db.base import *

# Create FastAPI app with metadata
app = FastAPI(
    title="Music Streaming API",
    description="Backend API for the Music Player App",
    version="0.1.0"
)

# Register global exception handlers
app.add_exception_handler(PasswordVerificationError, password_verification_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(JWTExpiredError, jwt_expired_exception_handler)
app.add_exception_handler(JWTDecodeError, jwt_decode_exception_handler)

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router

# Include routers with proper prefixes and tags
app.include_router(
    auth_router, prefix="/auth", tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)

app.include_router(
    user_router, tags=["users"], prefix="/user",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "User not found"}
    }
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint -- I saw this on a median post
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Music Player API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "authentication": "/auth",
            "users": "/users",
            "health": "/health"
        }
    }

