"""Kosmo - Cosmology Research Agent"""

__version__ = "1.0.0"

from .agent import KosmoAgent
from .cli import main as cli_main
from .errors import (
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    KosmoError,
)

__all__ = [
    "KosmoAgent",
    "cli_main",
    "__version__",
    "KosmoError",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorHandler",
]
