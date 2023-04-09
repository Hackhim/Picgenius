"""Module for Template class declaration."""
# import os
# from typing import Optional
#
# from PIL import Image
#
# from .watermark import Watermark
# from .design import Design
# from . import processing as im
# from . import utils


from dataclasses import dataclass
from typing import Optional

from .watermark import Watermark


@dataclass
class TemplateElement:
    """Template element data."""

    position: tuple[int, int]
    size: tuple[int, int]


@dataclass
class Template:
    """
    Template has the responsibility to apply the given design(s) on the template,
    and apply watermark if needed.
    """

    path: str
    elements: list[TemplateElement]
    watermark: Optional[Watermark] = None


#    def __init__(
#        self,
#        template_path: str,
#        elements: list[dict],
#        watermark: Optional[Watermark] = None,
#    ) -> None:
#        if not os.path.exists(template_path) or not os.path.isfile(template_path):
#            raise ValueError("Incorrect template path.")
#
#        self.path = template_path
#        _, self.name = utils.extract_filename(template_path)
#        self.elements = elements
#        self.count_elements = len(elements)
#        self.watermark = watermark
#
#    def generate_template(self, designs: list[Design]) -> Image.Image:
#        """Fits the designs in the template, and apply optional watermark."""
#        assert len(designs) == self.count_elements
#
#        template = Image.open(self.path)
#
#        for design, element in zip(designs, self.elements):
#            position = element["position"]
#            size = element["size"]
#            self.fit_design_in_template(template, design.image, position, size)
#
#        if self.watermark is not None:
#            template = self.watermark.apply_watermarking(template)
#
#        return template
#
#    def fit_design_in_template(
#        self,
#        template: Image.Image,
#        design: Image.Image,
#        position: tuple[int, int],
#        size: tuple[int, int],
#    ) -> Image.Image:
#        """Paste the specified design on the specified template."""
#        resized_design = im.resize_and_crop(design, *size)
#        template.paste(resized_design, position)
#        return template
