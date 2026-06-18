"""Database connection stub."""
from contextlib import contextmanager


@contextmanager
def get_db():
    """Get database connection (stub)."""
    raise NotImplementedError("Database not configured")
    yield  # pragma: no cover