"""
Logging configuration for StudyMate AI backend.
Provides standardized logging without exposing sensitive data.
"""
import logging
import re
import sys
from typing import Optional

SENSITIVE_PATTERNS = [
    re.compile(r'(password\s*[:=]\s*)[^\s,]+', re.IGNORECASE),
    re.compile(r'(api[-_]?key\s*[:=]\s*)[^\s,]+', re.IGNORECASE),
    re.compile(r'(token\s*[:=]\s*)[^\s,]+', re.IGNORECASE),
    re.compile(r'(bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*', re.IGNORECASE),
    re.compile(r'(secret\s*[:=]\s*)[^\s,]+', re.IGNORECASE),
]


class RedactingFilter(logging.Filter):
    """Filter that sanitizes sensitive information from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.msg)
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(r'\1[REDACTED]', msg)
        record.msg = msg
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """Configures root logger with clean formatting and redaction filter."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.addFilter(RedactingFilter())
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    handler.addFilter(RedactingFilter())

    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger with proper configuration."""
    setup_logging()
    return logging.getLogger(f"studymate.{name}")
