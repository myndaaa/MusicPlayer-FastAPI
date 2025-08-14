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
from app.api.v1.artist import router as artist_router
from app.api.v1.band import router as band_router
from app.api.v1.artist_band_member import router as artist_band_member_router
from app.api.v1.genre import router as genre_router
from app.api.v1.song import router as song_router
from app.api.v1.like import router as like_router
from app.api.v1.following import router as following_router
from app.api.v1.history import router as history_router
from app.api.v1.playlist import router as playlist_router
from app.api.v1.playlist_song import router as playlist_song_router
from app.api.v1.playlist_collaborator import router as playlist_collaborator_router
from app.api.v1.upload import router as upload_router
from app.api.v1.stream import router as stream_router
from app.api.v1.album import router as album_router
from app.api.v1.album_song import router as album_song_router
from app.api.v1.email import router as email_router

# Include routers with proper prefixes and tags
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(user_router, tags=["users"], prefix="/user")
app.include_router(artist_router, tags=["artists"], prefix="/artist")
app.include_router(band_router, tags=["bands"], prefix="/band")
app.include_router(artist_band_member_router, tags=["artist-band-members"], prefix="/artist-band-member")
app.include_router(genre_router, tags=["genres"], prefix="/genre")
app.include_router(song_router, tags=["songs"], prefix="/song")
app.include_router(like_router, tags=["likes"], prefix="/like")
app.include_router(following_router, tags=["following"], prefix="/following")
app.include_router(history_router, tags=["history"], prefix="/history")
app.include_router(playlist_router, tags=["playlists"], prefix="/playlist")
app.include_router(playlist_song_router, tags=["playlist-songs"], prefix="/playlist")
app.include_router(playlist_collaborator_router, tags=["playlist-collaborators"], prefix="/playlist")
app.include_router(upload_router, tags=["uploads"], prefix="/upload")
app.include_router(stream_router, tags=["streaming"], prefix="/stream")
app.include_router(album_router, tags=["albums"], prefix="/album")
app.include_router(album_song_router, tags=["album-songs"], prefix="/album")
app.include_router(email_router, tags=["email"], prefix="/auth")

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
            "users": "/user",
            "artists": "/artist",
            "bands": "/band",
            "artist-band-members": "/artist-band-member",
            "genres": "/genre",
            "songs": "/song",
            "likes": "/like",
            "following": "/following",
            "history": "/history",
            "playlists": "/playlist",
            "albums": "/album",
            "uploads": "/upload",
            "streaming": "/stream",
            "health": "/health"
        }
    }

