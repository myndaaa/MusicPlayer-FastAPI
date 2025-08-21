from app.services.email_service import EmailService


_email_service_singleton = EmailService()

def get_email_service() -> EmailService:
    """Provide a singleton EmailService instance"""
    return _email_service_singleton


