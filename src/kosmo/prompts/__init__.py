"""Kosmo prompts for the ReAct agent."""

from .cosmology_templates import (
    CMB_CONTEXT,
    CMB_KEYWORDS,
    DARK_MATTER_CONTEXT,
    DARK_MATTER_KEYWORDS,
    EXOPLANET_CONTEXT,
    EXOPLANET_KEYWORDS,
    detect_topic,
    enhance_prompt_for_topic,
    get_topic_context,
)
from .react_prompt import REACT_HUMAN_PROMPT, REACT_SYSTEM_PROMPT

__all__ = [
    "REACT_SYSTEM_PROMPT",
    "REACT_HUMAN_PROMPT",
    "DARK_MATTER_CONTEXT",
    "EXOPLANET_CONTEXT",
    "CMB_CONTEXT",
    "DARK_MATTER_KEYWORDS",
    "EXOPLANET_KEYWORDS",
    "CMB_KEYWORDS",
    "detect_topic",
    "get_topic_context",
    "enhance_prompt_for_topic",
]
