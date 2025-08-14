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
from app.services.token_service import TokenService
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


@router.get("/reset-password")
async def reset_password_page(
    token: str = Query(..., description="Reset token from email"),
    db: Session = Depends(get_db)
):
    """
    Password reset page - shows HTML form for password reset
    """
    # Check if token is valid
    reset_token = TokenService.get_valid_token(db, token, "password_reset")
    
    if not reset_token:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reset Failed - Music App</title>
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
                <h1>❌ Reset Failed</h1>
                <p>Invalid, expired, or already used reset token.</p>
                <a href="http://localhost:3000" class="btn">Go to Login</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # Token is valid, show password reset form
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reset Password - Music App</title>
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
                max-width: 400px;
                width: 100%;
            }}
            h1 {{
                color: #4CAF50;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 20px;
                text-align: left;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            input[type="password"] {{
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
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
                border: none;
                cursor: pointer;
                font-size: 16px;
            }}
            .btn:hover {{
                background: #45a049;
            }}
            .error {{
                color: #ff4757;
                margin-top: 10px;
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Reset Password</h1>
            <p>Enter your new password below:</p>
            
            <form id="resetForm">
                <div class="form-group">
                    <label for="newPassword">New Password:</label>
                    <input type="password" id="newPassword" name="newPassword" required 
                           minlength="8" placeholder="Enter new password">
                </div>
                
                <div class="form-group">
                    <label for="confirmPassword">Confirm Password:</label>
                    <input type="password" id="confirmPassword" name="confirmPassword" required 
                           minlength="8" placeholder="Confirm new password">
                </div>
                
                <button type="submit" class="btn">Reset Password</button>
            </form>
            
            <div id="error" class="error"></div>
        </div>
        
        <script>
            document.getElementById('resetForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const errorDiv = document.getElementById('error');
                
                if (newPassword !== confirmPassword) {{
                    errorDiv.textContent = 'Passwords do not match!';
                    errorDiv.style.display = 'block';
                    return;
                }}
                
                if (newPassword.length < 8) {{
                    errorDiv.textContent = 'Password must be at least 8 characters long!';
                    errorDiv.style.display = 'block';
                    return;
                }}
                
                try {{
                    const response = await fetch('/auth/reset-password', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            token: '{token}',
                            new_password: newPassword
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        alert('Password reset successfully! You can now login with your new password.');
                        window.location.href = 'http://localhost:3000';
                    }} else {{
                        errorDiv.textContent = result.detail || 'Password reset failed!';
                        errorDiv.style.display = 'block';
                    }}
                }} catch (error) {{
                    errorDiv.textContent = 'An error occurred. Please try again.';
                    errorDiv.style.display = 'block';
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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
