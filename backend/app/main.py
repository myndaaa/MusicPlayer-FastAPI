# Entry point for the FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Music Streaming API",
    description="Backend API for the Music Player App",
    version="0.1.0"
)
# Routers Imports


# Router inclusion and prefix declaration



# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# dev health check route
@app.get("/")
def read_root():
    return {"status": "API is live 🚀"}

# Test

from app.core.config import settings

print(settings.DATABASE_URL)
print(settings.JWT_SECRET_KEY)
