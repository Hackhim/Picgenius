"""Module for Video class declaration."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoSettings:
    """Video has the responsibility to generate a short video for the given design."""

    movement: str
    step: int = 1
    frames: int = 100
    fps: int = 24
    start_zoom: Optional[str] = None

    _AVAILABLE_MOVEMENTS: list[str] = [
        "zoom_in",
        "zoom_out",
        "slide_left",
        "slide_right",
        "random",
    ]
