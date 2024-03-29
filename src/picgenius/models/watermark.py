"""Module for Watermark class declaration."""
from typing import Optional, ClassVar

from dataclasses import dataclass


@dataclass
class Textbox:
    """Textbox data."""

    padding: tuple[int, int, int, int]
    color: tuple[int, int, int, int]

    def __post_init__(self):
        self.padding = tuple(self.padding)
        self.color = tuple(self.color)


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

    def __post_init__(self):
        self.color = tuple(self.color)
        self.position = tuple(self.position)

        if isinstance(self.position[0], str):
            assert (
                self.position[0] in self.AVAILABLE_X_POS
            ), f"Position {self.position[0]} is not available."
        if isinstance(self.position[1], str):
            assert (
                self.position[1] in self.AVAILABLE_Y_POS
            ), f"Position {self.position[1]} is not available."
