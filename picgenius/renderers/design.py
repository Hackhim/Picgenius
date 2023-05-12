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
    def upscale_design(design: Design, scale: int, cpu: bool = False) -> Image.Image:
        """Generate upscaled design."""
        assert scale in [2, 4, 8, 10, 12, 16]

        image = Image.open(design.path)
        if scale == 16:
            upscaled_image = im.upscale_image(image, 2, cpu=cpu)
            upscaled_image = im.upscale_image(upscaled_image, 8, cpu=cpu)
        elif scale == 12:
            upscaled_image = im.upscale_image(image, 4, cpu=cpu)
            width, height = upscaled_image.size
            upscaled_image = upscaled_image.resize(
                (width * 3 // 4, height * 3 // 4), Image.ANTIALIAS
            )
            upscaled_image = im.upscale_image(upscaled_image, 4, cpu=cpu)
        elif scale == 10:
            upscaled_image = im.upscale_image(image, 4, cpu=cpu)
            width, height = upscaled_image.size
            upscaled_image = upscaled_image.resize(
                (width * 5 // 8, height * 5 // 8), Image.ANTIALIAS
            )
            upscaled_image = im.upscale_image(upscaled_image, 4, cpu=cpu)
        else:
            upscaled_image = im.upscale_image(image, scale, cpu=cpu)

        return upscaled_image

    @staticmethod
    def _try_upscale_image(image: Image.Image, scale: int):
        pass
