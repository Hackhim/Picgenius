"""Module for WatermarkRenderer class declaration."""
from PIL import Image

from picgenius.models import Watermark, Textbox
from picgenius import processing as im


class WatermarkRenderer:
    """Apply watermarking"""

    @staticmethod
    def apply_watermarking(image: Image.Image, watermark: Watermark) -> Image.Image:
        """Read and applies the watermarking on the image."""

        width = WatermarkRenderer._calculate_width(image.width, watermark)
        font = im.find_font_size(watermark.text, watermark.font_path, width)

        textbox_kwargs = WatermarkRenderer._get_text_box_kwargs(watermark.textbox)

        text_position = WatermarkRenderer._get_text_position(
            image.size, im.get_text_size(font, watermark.text), watermark
        )

        watermarked = im.paste_text_on_image(
            image,
            watermark.text,
            font,
            text_position,
            color=watermark.color,
            **textbox_kwargs,
        )
        return watermarked

    @staticmethod
    def _calculate_width(image_width: int, watermark: Watermark) -> int:
        """Calculate the width of the watermark according to the image_width."""
        if isinstance(watermark.width, str) and watermark.width.endswith("%"):
            percentage = int(watermark.width.strip("%")) / 100
            width = int(image_width * percentage)
        else:
            width = int(watermark.width)
        return width

    @staticmethod
    def _get_text_box_kwargs(textbox: Textbox | None):
        if textbox is None:
            return {}
        else:
            return {
                "textbox_color": textbox.color,
                "textbox_padding": textbox.padding,
            }

    @staticmethod
    def _get_text_position(
        image_size: tuple, text_size: tuple, watermark: Watermark
    ) -> tuple[int, int]:
        """Returns the position X Y where to place the text."""

        x_pos = watermark.position[0]
        y_pos = watermark.position[1]

        if isinstance(x_pos, str) and x_pos in Watermark.AVAILABLE_X_POS:
            if x_pos == "center":
                x_pos = (image_size[0] - text_size[0]) // 2
            elif x_pos == "right":
                x_pos = image_size[0] - text_size[0] - watermark.margin
            else:
                x_pos = 0 + watermark.margin
        else:
            x_pos = int(x_pos)

        if isinstance(y_pos, str) and y_pos in Watermark.AVAILABLE_Y_POS:
            if y_pos == "center":
                y_pos = (image_size[1] - text_size[1]) // 2
            elif y_pos == "bottom":
                y_pos = image_size[1] - text_size[1] - watermark.margin
            else:
                y_pos = 0 + watermark.margin
        else:
            y_pos = int(y_pos)

        return (x_pos, y_pos)
