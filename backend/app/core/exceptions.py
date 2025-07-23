from fastapi import HTTPException, status

class PasswordVerificationError(HTTPException):
    """
    Custom exception for password verification failure.
    """
    def __init__(self, detail: str = "Password verification failed."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
