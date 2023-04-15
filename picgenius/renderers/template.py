"""Module for TemplateRenderer class declaration."""
from typing import Generator
from PIL import Image

from picgenius import processing as im
from picgenius.models import Template, Design
from picgenius.renderers import WatermarkRenderer


class TemplateRenderer:
    """
    A class that provides methods to render design images into templates
    and apply watermarks.
    """

    @staticmethod
    def generate_templates(
        templates: list[Template], designs: list[Design]
    ) -> Generator:
        """Generate all templates for the given list of designs."""
        design_index = 0
        for template in templates:
            design_index, next_designs = TemplateRenderer._get_next_designs(
                designs,
                design_index,
                len(template.elements),
            )
            yield (TemplateRenderer.generate_template(template, next_designs), template)

    @staticmethod
    def _get_next_designs(
        designs: list[Design], start_index: int, n_designs: int
    ) -> tuple[int, list[Design]]:
        """Returns the next n designs starting from self.design_index."""
        assert n_designs > 0
        designs_count = len(designs)
        design_index = start_index
        next_designs = []

        for _ in range(n_designs):
            next_designs.append(designs[design_index])
            design_index = (design_index + 1) % designs_count
        return (design_index, next_designs)

    @staticmethod
    def generate_template(template: Template, designs: list[Design]) -> Image.Image:
        """
        Fits the designs in the template, and apply optional watermark.

        Args:
            template (Template): The template object to render the designs onto.
            designs (list[Design]): A list of design objects to render.

        Returns:
            Image.Image: The generated image with designs fitted into the template.
        """
        template_image = Image.open(template.path)

        for design, element in zip(designs, template.elements):
            position = element.position
            size = element.size

            design_image = Image.open(design.path)
            TemplateRenderer._fit_design_in_template(
                template_image, design_image, position, size
            )

        if template.watermark is not None:
            template_image = WatermarkRenderer.apply_watermarking(
                template_image, template.watermark
            )

        return template_image

    @staticmethod
    def _fit_design_in_template(
        template: Image.Image,
        design: Image.Image,
        position: tuple[int, int],
        size: tuple[int, int],
    ) -> Image.Image:
        """
        Paste the specified design on the specified template.

        Args:
            template (Image.Image): The template image to paste the design onto.
            design (Image.Image): The design image to be pasted.
            position (tuple[int, int]): The X and Y coordinates for the design's position
            in the template.
            size (tuple[int, int]): The desired width and height for the design image.

        Returns:
            Image.Image: The template image with the design pasted.
        """
        resized_design = im.resize_and_crop(design, *size)
        template.paste(resized_design, position)
        return template
