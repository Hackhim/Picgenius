"""Module to define image processing functions."""
import os
import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import numpy as np


def resize_and_crop(image: Image.Image, size_x: int, size_y: int):
    """Resize and crop image."""
    target_ratio = size_x / size_y
    current_ratio = image.width / image.height
    if current_ratio > target_ratio:
        # Image is wider than aspect ratio, crop the sides
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2
        right = left + new_width
        box = (left, 0, right, image.height)
    else:
        # Image is taller than aspect ratio, crop the top and bottom
        new_height = int(image.width / target_ratio)
        top = (image.height - new_height) // 2
        bottom = top + new_height
        box = (0, top, image.width, bottom)

    cropped_design = image.crop(box)
    resized_design = cropped_design.resize((size_x, size_y))
    return resized_design


def paste_text_on_image(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    pos: tuple[int, int],
    color: tuple[int, int, int, int] = (0, 0, 0, 100),
    textbox_color: Optional[tuple[int, int, int, int]] = None,
    textbox_padding: int | tuple[int, int] | tuple[int, int, int, int] = 0,
):
    """Paste given text onto the given image using the specified font and color."""

    mask = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)

    if textbox_color is not None:
        text_size = get_text_size(font, text)
        padding = _format_padding(textbox_padding)
        textbox_pos = (
            pos[0] - padding[0],
            pos[1] - padding[1],
            pos[0] + text_size[0] + padding[2],
            pos[1] + text_size[1] + padding[3],
        )

        draw.rectangle(textbox_pos, fill=textbox_color)

    draw.text(pos, text, font=font, fill=color)

    combined = Image.alpha_composite(image, mask)
    return combined


def _format_padding(
    textbox_padding: int | tuple[int, int] | tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    if isinstance(textbox_padding, int):
        return tuple(textbox_padding for _ in range(4))
    elif isinstance(textbox_padding, tuple) and len(textbox_padding) == 2:
        top_and_bottom = textbox_padding[0]
        left_and_right = textbox_padding[1]
        return (left_and_right, top_and_bottom, left_and_right, top_and_bottom)
    elif isinstance(textbox_padding, tuple) and len(textbox_padding) == 4:
        return textbox_padding
    else:
        raise ValueError(f"textbox_padding must be an int or tuple.")


def find_font_size(text: str, font_path: str, max_width):
    """Return a font object that fits in the given size."""
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    while font.getlength(text) < max_width:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    return font


def generate_video_frames(image: Image.Image, frames: int = 100, step=1):
    """Generate the frames for the video."""
    images = []
    for i in range(0, frames, step):
        tl = i
        br = image.width - i

        zoom_region = (tl, tl, br, br)
        zoom_image = image.crop(zoom_region).resize(image.size, resample=Image.LANCZOS)
        images.append(zoom_image)
    return images


def get_text_size(font: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    """Returns the x, y size of a given font and text."""
    return font.getbbox(text)[-2:]
