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
        '''
        Usage:
        if not verify_password(...):
            raise PasswordVerificationError(detail="password oopsie! :(" )
        '''

class JWTDecodeError(HTTPException):
    def __init__(self, detail: str = "Invalid or malformed JWT token."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class JWTExpiredError(HTTPException):
    def __init__(self, detail: str = "JWT token has expired."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )
