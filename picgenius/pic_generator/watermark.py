"""Module for Watermark class declaration."""
import os
from typing import Optional
from PIL import Image
from .defaults import Defaults

from . import processing as im


class Watermark:
    """Watermark has the responsibility to apply the watermark on the given image."""

    AVAILABLE_X_POS = ["left", "center", "right"]
    AVAILABLE_Y_POS = ["top", "center", "bottom"]

    def __init__(
        self,
        font_path: str,
        text: str,
        color: tuple | list = Defaults.WATERMARK_TEXT_COLOR,
        position: tuple | list = Defaults.WATERMARK_POSITION,
        width: str | int = Defaults.WATERMARK_WIDTH,
        margin: int = 0,
        textbox: Optional[dict] = None,
    ) -> None:

        if not os.path.exists(font_path) or not os.path.isfile(font_path):
            raise ValueError("Incorrect font path.")
        self.font_path = font_path
        self.text = text
        self.color = tuple(color)
        self.position = tuple(position)
        self.width = width
        self.margin = margin
        self.textbox = textbox

    def apply_watermarking(self, image: Image.Image) -> Image.Image:
        """Read and applies the watermarking on the image."""

        width = self.calculate_width(image.width)
        font = im.find_font_size(self.text, self.font_path, width)

        textbox_kwargs = {}
        if self.textbox is not None:
            textbox_kwargs["textbox_color"] = tuple(self.textbox["color"])
            textbox_kwargs["textbox_padding"] = tuple(self.textbox["padding"])

        text_position = self.get_text_position(image.size, font.getsize(self.text))

        watermarked = im.paste_text_on_image(
            image, self.text, font, text_position, color=self.color, **textbox_kwargs
        )
        return watermarked

    def calculate_width(self, image_width: int) -> int:
        """Calculate the width of the watermark according to the image_width."""
        if isinstance(self.width, str) and self.width.endswith("%"):
            percentage = int(self.width.strip("%")) / 100
            width = int(image_width * percentage)
        else:
            width = int(self.width)
        return width

    def get_text_position(self, image_size: tuple, text_size: tuple) -> tuple[int, int]:
        """Returns the position X Y where to place the text."""

        x_pos = self.position[0]
        y_pos = self.position[1]

        if isinstance(x_pos, str) and x_pos in self.AVAILABLE_X_POS:
            if x_pos == "center":
                x_pos = (image_size[0] - text_size[0]) // 2
            elif x_pos == "right":
                x_pos = image_size[0] - text_size[0] - self.margin
            else:
                x_pos = 0 + self.margin
        else:
            x_pos = int(x_pos)

        if isinstance(y_pos, str) and y_pos in self.AVAILABLE_Y_POS:
            if y_pos == "center":
                y_pos = (image_size[1] - text_size[1]) // 2
            elif y_pos == "bottom":
                y_pos = image_size[1] - text_size[1] - self.margin
            else:
                y_pos = 0 + self.margin
        else:
            y_pos = int(y_pos)

        return (x_pos, y_pos)
