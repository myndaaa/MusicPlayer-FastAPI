import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from app.core.config import settings
from app.db.models.user import User
from typing import Optional


class EmailService:
    """Email service for sending verification and password reset emails"""
    
    def __init__(self):
        self.from_email = settings.FROM_EMAIL
        self.verification_base_url = settings.VERIFICATION_BASE_URL
        if settings.EMAIL_PROVIDER == "sendgrid" and settings.SENDGRID_API_KEY:
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        else:
            self.sg = None
    
    async def send_verification_email(self, user: User, token: str) -> bool:
        """Send email verification email"""
        verification_url = f"{self.verification_base_url}?token={token}"
        
        subject = "🎵 Verify Your Music App Account"
        html_content = self._create_verification_email_html(user, verification_url)
        
        return await self._send_email(user.email, subject, html_content)
    
    async def send_password_reset_email(self, user: User, token: str) -> bool:
        """Send password reset email"""
        reset_url = f"http://localhost:8000/auth/reset-password?token={token}"
        
        subject = "🔐 Reset Your Music App Password"
        html_content = self._create_password_reset_email_html(user, reset_url)
        
        return await self._send_email(user.email, subject, html_content)
    
    def _create_verification_email_html(self, user: User, verification_url: str) -> str:
        """Create HTML content for verification email"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">🎵 Music App</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Welcome to the music streaming platform!</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Verify Your Email Address</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 25px;">
                    Hi <strong>{user.first_name}</strong>,<br><br>
                    Thank you for signing up! To complete your registration and start enjoying music, 
                    please verify your email address by clicking the button below.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; display: inline-block; font-weight: bold;
                              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                        ✅ Verify Email Address
                    </a>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;">
                        If the button doesn't work, copy and paste this link into your browser:
                    </p>
                    <p style="color: #667eea; font-size: 12px; word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                        {verification_url}
                    </p>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 25px;">
                    <strong>Important:</strong> This verification link will expire in 24 hours.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't create this account, please ignore this email.
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email from Music App. Please do not reply to this email.
                </p>
            </div>
        </div>
        """
    
    def _create_password_reset_email_html(self, user: User, reset_url: str) -> str:
        """Create HTML content for password reset email"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 30px; border-radius: 10px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">🔐 Music App</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Password Reset Request</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Reset Your Password</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 25px;">
                    Hi <strong>{user.first_name}</strong>,<br><br>
                    We received a request to reset your password. Click the button below to create a new password.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; display: inline-block; font-weight: bold;
                              box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);">
                        🔐 Reset Password
                    </a>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <p style="color: #666; font-size: 14px;">
                        If the button doesn't work, copy and paste this link into your browser:
                    </p>
                    <p style="color: #dc3545; font-size: 12px; word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                        {reset_url}
                    </p>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 25px;">
                    <strong>Important:</strong> This reset link will expire in 1 hour.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't request a password reset, please ignore this email.
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email from Music App. Please do not reply to this email.
                </p>
            </div>
        </div>
        """
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using configured provider"""
        if settings.EMAIL_PROVIDER == "sendgrid" and self.sg:
            return await self._send_sendgrid_email(to_email, subject, html_content)
        else:
            return await self._send_console_email(to_email, subject, html_content)
    
    async def _send_sendgrid_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            print(f"Email sent successfully to {to_email}")
            print(f"SendGrid Status Code: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            print(f"Failed to send email via SendGrid: {str(e)}")
            return False
    
    async def _send_console_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Log email to console for development"""
        print("\n" + "="*60)
        print("EMAIL SENT (Console Output)")
        print("="*60)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"From: {self.from_email}")
        print("="*60)
        print("HTML Content:")
        print(html_content)
        print("="*60)
        print("This email would be sent in production!")
        print("="*60 + "\n")
        return True
