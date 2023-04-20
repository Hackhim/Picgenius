"""Module to define image processing functions."""
from typing import Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops


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
        raise ValueError("textbox_padding must be an int or tuple.")


def find_font_size(text: str, font_path: str, max_width):
    """Return a font object that fits in the given size."""
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    while font.getlength(text) < max_width:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    return font


def get_text_size(font: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    """Returns the x, y size of a given font and text."""
    return font.getbbox(text)[-2:]


def find_coeffs(source_coords, target_coords):
    """Find transform coeffs."""
    matrix = []
    for s, t in zip(source_coords, target_coords):
        matrix.extend(
            [
                [t[0], t[1], 1, 0, 0, 0, -s[0] * t[0], -s[0] * t[1]],
                [0, 0, 0, t[0], t[1], 1, -s[1] * t[0], -s[1] * t[1]],
            ]
        )

    A = np.array(matrix, dtype=np.float32)
    B = np.array(source_coords, dtype=np.float32).reshape(8)

    res = np.linalg.solve(A, B)
    return np.array(res).reshape(8)


def perspective_transform(image, coeffs):
    """Apply the coeffs transform."""
    width, height = image.size
    return image.transform(
        (width, height), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC
    )


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    """Apply a basic filter."""
    filter_map = {
        "BLUR": ImageFilter.BLUR,
        "CONTOUR": ImageFilter.CONTOUR,
        "DETAIL": ImageFilter.DETAIL,
        "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
        "EMBOSS": ImageFilter.EMBOSS,
        "SHARPEN": ImageFilter.SHARPEN,
        "SMOOTH": ImageFilter.SMOOTH,
        "SMOOTH_MORE": ImageFilter.SMOOTH_MORE,
    }

    if filter_name in filter_map:
        filter_obj = filter_map[filter_name]
        return image.filter(filter_obj)
    else:
        raise ValueError(f"Unknown filter: {filter_name}")


def smooth_integration(transformed_image, corner_points, cut_pixels=3, smooth_power=1):
    """Add smooth transition."""
    # Duplicate the transformed image
    background_image = transformed_image.copy()
    foreground_image = transformed_image.copy()

    # Apply Gaussian blur to the background image
    for _ in range(smooth_power):
        background_image = apply_filter(background_image, "SMOOTH_MORE")

    # Calculate the new corner points for the mask
    tl, tr, bl, br = corner_points
    new_tl = (tl[0] + cut_pixels, tl[1] + cut_pixels)
    new_tr = (tr[0] - cut_pixels, tr[1] + cut_pixels)
    new_bl = (bl[0] + cut_pixels, bl[1] - cut_pixels)
    new_br = (br[0] - cut_pixels, br[1] - cut_pixels)
    new_corner_points = [new_tl, new_tr, new_br, new_bl]

    # Create a mask with the new corner points
    mask = Image.new("L", foreground_image.size, 0)
    ImageDraw.Draw(mask).polygon(new_corner_points, outline=255, fill=255)

    # Paste the foreground image onto the background image using the mask
    result_image = Image.composite(foreground_image, background_image, mask)

    return result_image
