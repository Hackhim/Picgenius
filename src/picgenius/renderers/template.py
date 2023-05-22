"""Module for TemplateRenderer class declaration."""
from typing import Generator, Optional
from PIL import Image


from picgenius import processing as im
from picgenius.models import Template, TemplateElement, Design, TemplateImageElement
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
                template, designs, design_index
            )
            yield (TemplateRenderer.generate_template(template, next_designs), template)

    @staticmethod
    def _get_next_designs(
        template: Template, designs: list[Design], start_index: int
    ) -> tuple[int, list[Design]]:
        """Returns the next n designs starting from self.design_index."""
        designs_count = len(designs)
        design_index = start_index
        next_designs = []
        n_elements = len(template.elements)

        if template.repeat:
            next_designs.extend(designs[design_index] for _ in range(n_elements))
            design_index = (design_index + 1) % designs_count
        else:
            for _ in range(n_elements):
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

        template_image = TemplateRenderer._create_template_image(template)

        for design, element in zip(designs, template.elements):
            design_image = design.load_image()
            design_image = TemplateRenderer._design_pre_treatment(design_image, element)

            template_image = TemplateRenderer._template_element_integration(
                template_image,
                design_image,
                element,
            )

        for image_element in template.images:
            TemplateRenderer.paste_image_on_template_image(
                template_image, image_element
            )

        for watermark in template.watermarks:
            template_image = WatermarkRenderer.apply_watermarking(
                template_image, watermark
            )

        return template_image

    @staticmethod
    def _create_template_image(template: Template) -> Image.Image:
        if template.path is not None:
            return Image.open(template.path)
        else:
            return Image.new("RGBA", template.size, template.background_color)

    @staticmethod
    def _design_pre_treatment(
        image: Image.Image, element: TemplateElement
    ) -> Image.Image:
        image = TemplateRenderer._apply_ratio(image, element)
        image = TemplateRenderer._apply_zoom(image, element)
        image = TemplateRenderer._apply_overlay(image, element)
        image = TemplateRenderer._apply_transparency(image, element)
        return image

    @staticmethod
    def _apply_ratio(image: Image.Image, element: TemplateElement) -> Image.Image:
        if element.ratio is not None:
            return im.crop_to_ratio(image, element.ratio)
        return image

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
    def _apply_transparency(image: Image.Image, element: TemplateElement):
        if element.transparency is not None and element.transparency < 1.0:
            image = image.convert("RGBA")
            image.putalpha(int(element.transparency * 255))
            image.paste(image, (0, 0), image)
        return image

    @staticmethod
    def _template_element_integration(
        template_image: Image.Image, design_image: Image.Image, element: TemplateElement
    ) -> Image.Image:
        position = element.position
        size = element.size
        width = element.width
        height = element.height

        design_width, design_height = design_image.size
        aspect_ratio = design_width / design_height

        if size is not None:
            width, height = size
        elif width is None and height is not None:
            width = int(height * aspect_ratio)
        elif width is not None and height is None:
            height = int(width / aspect_ratio)
        else:
            width, height = (design_width, design_height)

        if len(position) == 2:
            return TemplateRenderer._fit_design_in_template(
                template_image, design_image, position, (width, height)
            )
        elif len(position) == 4:
            return TemplateRenderer._fit_design_in_transformed_template(
                template_image, design_image, position
            )
        else:
            raise ValueError(
                f"Invalid position value ({position}) for element: {element}."
            )

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
        if resized_design.mode == "RGBA":
            template.paste(resized_design, position[:], resized_design)
        else:
            template.paste(resized_design, position[:])
        return template

    @staticmethod
    def _fit_design_in_transformed_template(
        template: Image.Image,
        design: Image.Image,
        position: tuple[
            tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
        ],
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

    @staticmethod
    def paste_image_on_template_image(
        template_image: Image.Image, image_element: TemplateImageElement
    ):
        """Paste the image element on the specified template image."""
        image = image_element.load_image()
        image_size = TemplateRenderer._calculate_image_element_size(
            image_element, image.size, template_image.size
        )
        image = image.resize(image_size, Image.ANTIALIAS)

        if image_element.transparency < 1.0:
            tmp_image = image.copy()
            tmp_image.putalpha(int(image_element.transparency * 255))
            image.paste(tmp_image, (0, 0), image)

        image_position = TemplateRenderer._calculate_image_element_position(
            image_element, image.size, template_image.size
        )
        return template_image.paste(image, image_position[:], image)

    @staticmethod
    def _calculate_image_element_size(
        image_element: TemplateImageElement,
        image_element_size: tuple[int, int],
        template_image_size: tuple[int, int],
    ) -> tuple[int, int]:
        """Calculate the size of the image element."""
        template_width, template_height = template_image_size
        image_element_width, image_element_height = image_element_size
        aspect_ratio = image_element_width / image_element_height

        width = None
        height = None

        if isinstance(image_element.width, str) and image_element.width.endswith("%"):
            percentage = int(image_element.width.strip("%")) / 100
            width = int(template_width * percentage)
        elif isinstance(image_element.width, (str, int, float)):
            width = int(image_element.width)

        if isinstance(image_element.height, str) and image_element.height.endswith("%"):
            percentage = int(image_element.height.strip("%")) / 100
            height = int(template_height * percentage)
        elif isinstance(image_element.height, (str, int, float)):
            height = int(image_element.height)

        if width is None and height is not None:
            width = int(height * aspect_ratio)
        elif width is not None and height is None:
            height = int(width / aspect_ratio)
        else:
            width, height = (image_element_width, image_element_height)

        return (width, height)

    @staticmethod
    def _calculate_image_element_position(
        image_element: TemplateImageElement,
        image_element_size: tuple[int, int],
        template_image_size: tuple[int, int],
    ) -> tuple[int, int]:
        """Calculate the position of the image element."""

        image_element_width, image_element_height = image_element_size
        template_width, template_height = template_image_size
        x_pos = image_element.position[0]
        y_pos = image_element.position[1]
        margin = image_element.margin

        if isinstance(x_pos, str):
            if x_pos == "center":
                x_pos = (template_width - image_element_width) // 2
            elif x_pos == "right":
                x_pos = template_width - image_element_width - margin
            else:
                x_pos = 0 + margin
        else:
            x_pos = int(x_pos)

        if isinstance(y_pos, str):
            if y_pos == "center":
                y_pos = (template_height - image_element_height) // 2
            elif y_pos == "bottom":
                y_pos = template_height - image_element_height - margin
            else:
                y_pos = 0 + margin
        else:
            y_pos = int(y_pos)

        return (x_pos, y_pos)
