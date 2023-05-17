"""Module for Video class declaration."""
from dataclasses import dataclass, field
from typing import ClassVar
from picgenius.models import Watermark


@dataclass
class VideoSettings:
    """Video has the responsibility to generate a short video for the given design."""

    movement: str
    step: int = 1
    frames: int = 100
    fps: int = 24
    format: tuple[int, int] = (2000, 2000)
    start_zoom: int = 100
    watermarks: list[Watermark] = field(default_factory=list)

    _AVAILABLE_MOVEMENTS: ClassVar[list[str]] = [
        "zoom_in",
        "zoom_out",
        "slide_left",
        "slide_right",
        "random",
    ]

    def __post_init__(self):
        if self.movement not in self._AVAILABLE_MOVEMENTS:
            raise AttributeError(f"{self.movement} isn't a valid value.")
