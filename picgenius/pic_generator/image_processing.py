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
    color: tuple[int, int, int, int] = (0, 0, 0, 0),
):
    """
    Paste given text onto the given image using the specified font and color.

    Args:
        image (PIL.Image.Image): The image onto which to paste the text.
        text (str): The text to paste onto the image.
        font (PIL.ImageFont.FreeTypeFont): The font to use for the text.
        color (tuple[int, int, int, int], optional):
            The color of the text, as a tuple of RGBA values. Defaults to (0, 0, 0, 0).

    Returns:
        PIL.Image.Image: The resulting image with the text pasted onto it.
    """
    mask = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = (
        (image.width - text_bbox[2]) // 2,
        (image.height - text_bbox[3]) // 2,
    )

    draw.text(text_position, text, font=font, fill=color)
    combined = Image.alpha_composite(image, mask)
    return combined


def get_watermarking_font(image: Image.Image, text: str, font_path: str, margin: int):
    """
    Return a font object that can be used to apply watermarking text to an image.

    Args:
        image (PIL.Image.Image): The image to be watermarked.
        text (str): The text to be used as watermark.
        font_path (str): The path of the font file to be used for watermarking.
        margin (int): The margin size to be used when applying the watermark.

    Returns:
        PIL.ImageFont.FreeTypeFont: A font object that can be used to apply
        watermarking text to an image.
    """
    max_width = image.width - (margin * 2)
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    while font.getlength(text) < max_width:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    return font


def generate_video_frames(self, image: Image.Image, frames: int = 100, step=1):
    """Generate the frames for the video."""
    images = []
    for i in range(0, frames, step):
        tl = i
        br = image.width - i

        zoom_region = (tl, tl, br, br)
        zoom_image = image.crop(zoom_region).resize(image.size, resample=Image.LANCZOS)
        images.append(zoom_image)
    return images
