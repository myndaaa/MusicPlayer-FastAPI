from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.custom_exception import PasswordVerificationError
from app.core.custom_exception import JWTExpiredError, JWTDecodeError


async def password_verification_exception_handler(request: Request, exc: PasswordVerificationError):
    """
    Handles PasswordVerificationError globally and returns a custom JSON response.
    Triggered when PasswordVerificationError is raised anywhere in the app.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": "PASSWORD_VERIFICATION_FAILED",
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles FastAPIs validation errors globally (eg. when a request payload is malformed).
    """
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles all other unhandled HTTP exceptions 
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

async def jwt_expired_exception_handler(request: Request, exc: JWTExpiredError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": "JWT_EXPIRED"},
    )

async def jwt_decode_exception_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": "JWT_DECODE_ERROR"},
    )
