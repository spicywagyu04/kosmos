"""Kosmo - Cosmology Research Agent"""

__version__ = "1.0.0"

from .agent import KosmoAgent
from .cli import main as cli_main

__all__ = ["KosmoAgent", "cli_main", "__version__"]
