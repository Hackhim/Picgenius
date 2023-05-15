"""Module for TemplateRenderer class declaration."""
from typing import Generator, Optional
from PIL import Image


from picgenius import processing as im
from picgenius.models import Template, TemplateElement, Design
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

        if template.path is not None:
            template_image = Image.open(template.path)
        else:
            template_image = Image.new("RGBA", template.size, template.background_color)

        for design, element in zip(designs, template.elements):
            position = element.position
            size = element.size

            design_image = Image.open(design.path)
            design_image = TemplateRenderer._apply_zoom(design_image, element)
            design_image = TemplateRenderer._apply_overlay(design_image, element)
            if len(position) == 2 and size is not None:
                TemplateRenderer._fit_design_in_template(
                    template_image, design_image, position, size
                )
            elif len(position) == 4:
                TemplateRenderer._fit_design_in_transformed_template(
                    template_image, design_image, position, element.ratio
                )
            else:
                raise ValueError(
                    f'Template "{template.name}" has incorrect elements values.'
                )

        if template.watermark is not None:
            template_image = WatermarkRenderer.apply_watermarking(
                template_image, template.watermark
            )

        return template_image

    @staticmethod
    def _apply_zoom(image: Image.Image, element: TemplateElement) -> Image.Image:
        if element.zoom is not None:
            return im.zoom(image, element.zoom, zoom_center=element.zoom_position)
        return image

    @staticmethod
    def _apply_overlay(image: Image.Image, element: TemplateElement) -> Image.Image:
        if element.overlay is not None:
            return im.apply_transparent_overlay(image, element.overlay)
        return image

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

    @staticmethod
    def _fit_design_in_transformed_template(
        template: Image.Image,
        design: Image.Image,
        position: tuple[
            tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
        ],
        ratio: Optional[tuple[int, int]] = None,
    ) -> Image.Image:
        """
        Paste the specified design on the specified transformed template.

        Args:
            template (Image.Image): The template image to paste the design onto.
            design (Image.Image): The design image to be pasted.
            position (tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]])
                The coordinates of the four corners
            of the design's position in the template.

        Returns:
            Image.Image: The template image with the design pasted.
        """
        working_design = design.copy()
        if ratio is not None:
            working_design = im.crop_to_ratio(working_design, ratio)
        working_design = im.proportional_overlap_resize(working_design, template)

        tl, tr, bl, br = position
        width, height = working_design.size
        input_points = [(0, 0), (width, 0), (0, height), (width, height)]
        output_points = [tl, tr, bl, br]
        coeffs = im.find_coeffs(input_points, output_points)

        transformed_design = im.perspective_transform(
            working_design.convert("RGBA"), coeffs
        )

        transformed_design = im.smooth_integration(
            transformed_design, output_points, smooth_power=2
        )

        template.paste(transformed_design, (0, 0), transformed_design)
        return template
