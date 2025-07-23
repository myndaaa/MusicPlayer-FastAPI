# Entry point for the FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Music Streaming API",
    description="Backend API for the Music Player App",
    version="0.1.0"
)

# Routers Imports
'''
from app.api.v1 import user_router, song_router, etc...
'''
# Router inclusion and prefix declaration
'''
app.include_router(user.router, prefix="/api/v1/users")
app.include_router(song.router, prefix="/api/v1/songs")
'''
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

