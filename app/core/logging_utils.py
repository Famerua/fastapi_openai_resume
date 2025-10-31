import logging

from app.core.config import settings


def configure_logging() -> None:
    """Configure the application-wide logging settings."""
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
