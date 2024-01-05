import uuid
from datetime import UTC, datetime


def utc_now() -> datetime:
    """Get the current time in UTC."""
    return datetime.now(UTC)


def gen_uuid() -> str:
    """Generate a uuid hex string."""
    return str(uuid.uuid4().hex)
