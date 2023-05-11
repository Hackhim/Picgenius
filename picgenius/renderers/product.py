"""Module for ProductRenderer class declaration."""
import random
import os
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

from picgenius import processing as im
from picgenius.models import Product, Design, Format
from picgenius.renderers import TemplateRenderer, VideoRenderer


class ProductRenderer:
    """ProductRenderer."""

    FORMATTED_DESIGNS_FOLDER = "formatted"
    VISUALS_FOLDER = "visuals"
    VIDEO_FILENAME = "video.mp4"

    @staticmethod
    def generate_templates(product: Product, output_dir: str, max_threads: int = 10):
        """Generate product templates."""

        def save_template(visual_template, template_name):
            output_path = os.path.join(output_dir, f"{template_name}.png")
            visual_template.save(output_path)

        output_dir = ProductRenderer.prepare_visuals_output_dir(output_dir, product)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for generated_visual, template in TemplateRenderer.generate_templates(
                product.type.templates, product.designs
            ):
                future = executor.submit(save_template, generated_visual, template.name)
                futures.append(future)

            # Wait for all threads to complete
            for future in as_completed(futures):
                future.result()

    @staticmethod
    def generate_video(
        product: Product,
        output_dir: str,
        design_index: int = 0,
        random_design: bool = False,
    ):
        """Generate product video."""
        if product.type.video_settings is None:
            return

        if random_design:
            design = random.choice(product.designs)
        else:
            design = product.designs[design_index]

        output_dir = ProductRenderer.prepare_visuals_output_dir(output_dir, product)
        output_path = os.path.join(output_dir, ProductRenderer.VIDEO_FILENAME)

        image = Image.open(design.path)
        video = VideoRenderer.generate_video(image, product.type.video_settings)
        video.write_videofile(output_path, verbose=False, logger=None)

    @staticmethod
    def generate_formatted_designs(
        product: Product, output_dir: str, max_threads: int = 10
    ):
        """Generate formatted designs."""

        def save_formatted_image(formatted_image, formatted_dir, filename):
            output_path = os.path.join(formatted_dir, filename)
            formatted_image.save(output_path)
            formatted_image.close()

        for design in product.designs:
            formats = product.type.formats
            design_name = design.name if len(formats) > 1 else ""

            formatted_dir = ProductRenderer.prepare_formatted_output_dir(
                output_dir, product, design_name
            )

            print("-" * 32)
            print(design.path)
            print(output_dir)

            formatted_designs = ProductRenderer._generate_formats_for_design(
                design,
                formats,
            )

            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = []
                for formatted_image, filename in formatted_designs:
                    future = executor.submit(
                        save_formatted_image, formatted_image, formatted_dir, filename
                    )
                    futures.append(future)

                # Wait for all threads to complete
                for future in as_completed(futures):
                    future.result()

    @staticmethod
    def _generate_formats_for_design(
        design: Design, design_formats: list[Format]
    ) -> Generator:
        """Generate formatted design."""
        image = Image.open(design.path)
        for design_format in design_formats:
            ppi = design_format.ppi
            inches_x, inches_y = design_format.inches
            size_in_pixels = (inches_x * ppi, inches_y * ppi)

            formatted_image = im.resize_and_crop(image, *size_in_pixels)
            filename = f"{design.name}-{inches_x}-{inches_y}.png"
            yield (formatted_image, filename)

    @staticmethod
    def prepare_formatted_output_dir(base_dir: str, product: Product, design_name: str):
        """Make dirs and return path."""
        output_dir = os.path.join(
            base_dir,
            product.name,
            ProductRenderer.FORMATTED_DESIGNS_FOLDER,
            design_name,
        )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    @staticmethod
    def prepare_visuals_output_dir(base_dir: str, product: Product):
        """Make dirs and return path."""
        output_dir = os.path.join(
            base_dir, product.name, ProductRenderer.VISUALS_FOLDER
        )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
