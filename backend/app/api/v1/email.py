from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.email import (
    EmailVerificationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse
)
from app.crud.email import EmailCRUD
from typing import Optional

router = APIRouter()


@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., description="Verification token from email"),
    db: Session = Depends(get_db)
):
    """
    Verify email address with token from email
    
    - **token**: Verification token received via email
    - Returns HTML page with success/error message
    """
    success, message, user = EmailCRUD.verify_email(db, token)
    
    if success:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verified - Music App</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #4CAF50;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 18px;
                    margin-bottom: 30px;
                }}
                .btn {{
                    background: #4CAF50;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    display: inline-block;
                    font-weight: bold;
                    transition: background 0.3s;
                }}
                .btn:hover {{
                    background: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ Email Verified Successfully!</h1>
                <p>Your email address has been verified. You can now log in to your account.</p>
                <a href="http://localhost:8000" class="btn">Go to Login</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification Failed - Music App</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #ff4757;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 18px;
                    margin-bottom: 30px;
                }}
                .btn {{
                    background: #ff4757;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    display: inline-block;
                    font-weight: bold;
                    transition: background 0.3s;
                }}
                .btn:hover {{
                    background: #ff3742;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Verification Failed</h1>
                <p>{message}</p>
                <a href="http://localhost:8000" class="btn">Go to Login</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification email
    
    - **email**: Email address to resend verification to
    - Always returns success message (for security, doesn't reveal if email exists)
    """
    success, message = await EmailCRUD.resend_verification_email(db, request.email)
    
    if success:
        return ResendVerificationResponse(message=message)
    else:
        raise HTTPException(status_code=500, detail=message)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Send password reset email
    
    - **email**: Email address to send reset link to
    - Always returns success message (for security, doesn't reveal if email exists)
    """
    success, message = await EmailCRUD.send_password_reset_email(db, request.email)
    
    if success:
        return ForgotPasswordResponse(message=message)
    else:
        raise HTTPException(status_code=500, detail=message)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    
    - **token**: Reset token from email
    - **new_password**: New password to set
    - Returns success message if password reset successful
    """
    success, message = EmailCRUD.reset_password(db, request.token, request.new_password)
    
    if success:
        return ResetPasswordResponse(message=message)
    else:
        raise HTTPException(status_code=400, detail=message)
