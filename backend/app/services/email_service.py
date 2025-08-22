import sendgrid
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from app.services.template_renderer import TemplateRenderer
from app.db.models.user import User


class EmailService:
    """Email service for SendGrid using file-based HTML templates."""

    def __init__(self, renderer: TemplateRenderer | None = None):
        self.from_email = settings.FROM_EMAIL
        self.verification_base_url = settings.VERIFICATION_BASE_URL
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.renderer = renderer or TemplateRenderer()

    def send_verification_email(self, user: User, token: str) -> bool:
        verification_url = f"{self.verification_base_url}?token={token}"
        subject = "🎵 Verify Your Music App Account"
        html_content = self.renderer.render(
            "app/templates/email/verification.html",
            {"first_name": user.first_name, "verification_url": verification_url},
        )
        return self._send(user.email, subject, html_content)

    def _send(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception:
            return False


