from datetime import UTC, datetime


def utc_now() -> datetime:
    """Get the current time in UTC."""
    return datetime.now(UTC)
