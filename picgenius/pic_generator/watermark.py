"""Module for Watermark class declaration."""
import os
from typing import Optional
from .defaults import Defaults


class Watermark:

    """Watermark has the responsibility to apply the watermark on the given image."""

    def __init__(
        self,
        font_path: str,
        text: str,
        color: list = Defaults.WATERMARK_TEXT_COLOR,
        position: list = Defaults.WATERMARK_POSITION,
        width: str | int = Defaults.WATERMARK_WIDTH,
        margin: int = 0,
        textbox: Optional[dict] = None,
    ) -> None:

        if not os.path.exists(font_path) or not os.path.isfile(font_path):
            raise ValueError("Incorrect font path.")
        self.font_path = font_path
        self.text = text
        self.color = color
        self.position = position
        self.width = width
        self.margin = margin
        self.textbox = textbox
