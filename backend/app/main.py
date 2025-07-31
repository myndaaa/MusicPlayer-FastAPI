# Entry point for the FastAPI application
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.custom_exception import PasswordVerificationError, JWTExpiredError, JWTDecodeError
from app.core.exception_handler import ( password_verification_exception_handler,validation_exception_handler,http_exception_handler,
jwt_expired_exception_handler, jwt_decode_exception_handler, jwt_decode_exception_handler )

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

# Routers Imports
from app.api.v1.auth import router as auth_router

# Router inclusion and prefix declaration
app.include_router(auth_router, prefix="/api/v1")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

