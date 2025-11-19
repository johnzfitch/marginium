"""
Visual Margin System for LLM Generation State Tracking

This package provides a system for tracking LLM generation state through
visual margin rendering, enabling better constraint satisfaction in
language model outputs.
"""

__version__ = "0.1.0"

from .generation_state_tracker import GenerationStateTracker
from .margin_renderer import MarginRenderer
from .visual_margin_generator import VisualMarginGenerator
from .constraint_parser import ConstraintParser

__all__ = [
    "GenerationStateTracker",
    "MarginRenderer",
    "VisualMarginGenerator",
    "ConstraintParser",
]
