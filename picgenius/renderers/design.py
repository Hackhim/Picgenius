"""Module for DesignRenderer class declaration."""
from typing import Generator
from PIL import Image


from picgenius import processing as im
from picgenius.models import Format, Design


class DesignRenderer:
    """A class that provides methods to render images based on designs."""

    @staticmethod
    def generate_design_formats(
        design: Design, design_formats: list[Format]
    ) -> Generator:
        """Generate formatted design."""
        image = Image.open(design.path)
        for design_format in design_formats:
            ppi = design_format.ppi
            inches_x, inches_y = design_format.inches
            size_in_pixels = (inches_x * ppi, inches_y * ppi)

            formatted_image = im.resize_and_crop(image, *size_in_pixels)
            filename = f"{design.name}-{inches_x}-{inches_y}"
            yield (formatted_image, filename)

    @staticmethod
    def upscale_design(design: Design, scale: int) -> Generator:
        """Generate upscaled design."""
        assert scale in [2, 4, 8, 16]

        image = Image.open(design.path)
        if scale == 16:
            upscaled_image = im.upscale_image(image, 2)
            upscaled_image = im.upscale_image(upscaled_image, 8)
        else:
            upscaled_image = im.upscale_image(image, scale)

        yield upscaled_image
