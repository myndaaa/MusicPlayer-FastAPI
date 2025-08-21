from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)

# duration in hours
EMAIL_VERIFICATION_TOKEN_HOURS: int = 24



