"""Module for Design class declaration."""
from PIL import Image

# from .defaults import Defaults
# from . import processing as im


class Design:
    """Design has the responsibility to generate its formatted images."""

    design_path: str
    name: str = ""

    # TODO: get name from design_path

    # def generate_formats(self, formats: list[dict]):
    #    """Generate all the formats."""


#
#    for _format in formats:
#        inches = _format.get("inches", Defaults.FORMAT_INCHES)
#        ppi = _format.get("ppi", Defaults.FORMAT_PPI)
#        yield (self.generate_one_format(inches, ppi), inches)
#
#    def generate_one_format(self, inches: tuple[int, int], ppi: int) -> Image.Image:
#       """Generate formatted image."""
#       size_x, size_y = inches
#       return im.resize_and_crop(self.image, size_x * ppi, size_y * ppi)
#
