"""Module for Watermark class declaration."""
from typing import Optional, ClassVar

from dataclasses import dataclass, field


@dataclass
class Textbox:
    """Textbox data."""

    padding: tuple[int, int, int, int]
    color: tuple[int, int, int, int]


@dataclass
class Watermark:
    """Watermark data."""

    font_path: str
    text: str
    color: tuple = (0, 0, 0, 255)
    position: tuple[int | str, int | str] = ("center", "center")
    width: str | int = "70%"
    margin: int = 0
    textbox: Optional[Textbox] = None

    AVAILABLE_X_POS: ClassVar[list[str]] = ["left", "center", "right"]
    AVAILABLE_Y_POS: ClassVar[list[str]] = ["top", "center", "bottom"]
