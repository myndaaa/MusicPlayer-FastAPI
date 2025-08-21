from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.email import (
    EmailVerificationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
)
from app.crud.email import EmailCRUD
from app.services.email_service import EmailService
from app.dependencies import get_email_service


router = APIRouter(prefix="/auth", tags=["email"])


@router.get("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    token: str = Query(..., description="Verification token from email"),
    db: Session = Depends(get_db),
):
    """
    Verify email address with token.
    Returns JSON only. The frontend gonna consume this and render UI.
    // TODO(frontend): This endpoint should be called from a frontend route /verify?token={token}
    """
    success, message, _ = EmailCRUD.verify_email(db, token)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return EmailVerificationResponse(message=message)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Resend verification email 
    // TODO(frontend): Trigger from a "Resend verification" button.
    """
    success, _ = EmailCRUD.resend_verification_email(db, request.email, email_service)
    if not success:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="Email delivery failed. Please try again later.")
    # Mask existence return generic message on success
    return ResendVerificationResponse(message="If the email exists, a verification link has been sent")

