"""Module for ProductRenderer class declaration."""
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

from picgenius.models import Product
from .template import TemplateRenderer
from .video import VideoRenderer
from .design import DesignRenderer


class ProductRenderer:
    """ProductRenderer."""

    FORMATTED_DESIGNS_FOLDER = "formatted"
    VISUALS_FOLDER = "visuals"
    VIDEO_FILENAME = "video.mp4"

    @staticmethod
    def generate_templates(product: Product, output_dir: str, max_threads: int = 10):
        """Generate product templates."""

        output_dir = ProductRenderer.prepare_visuals_output_dir(output_dir, product)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for generated_visual, template in TemplateRenderer.generate_templates(
                product.type.templates, product.designs
            ):
                future = executor.submit(
                    ProductRenderer.save_image,
                    generated_visual,
                    output_dir,
                    template.filename,
                )
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

        for design in product.designs:
            formats = product.type.formats
            design_name = design.name if len(formats) > 1 else ""

            formatted_dir = ProductRenderer.prepare_formatted_output_dir(
                output_dir, product, design_name
            )

            design_formats = DesignRenderer.generate_design_formats(
                design,
                formats,
            )

            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = []
                for formatted_image, filename in design_formats:
                    future = executor.submit(
                        ProductRenderer.save_image,
                        formatted_image,
                        formatted_dir,
                        f"{filename}.jpg",
                    )
                    futures.append(future)

                # Wait for all threads to complete
                for future in as_completed(futures):
                    future.result()

    @staticmethod
    def save_image(image: Image.Image, output_dir: str, filename: str):
        """Save image to output_dir."""
        output_path = os.path.join(output_dir, filename)
        image.save(output_path)
        image.close()

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