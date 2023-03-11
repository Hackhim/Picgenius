import os
import logging
from typing import Optional
from PIL import Image


class FormattedImageGenerator:
    def generate_formatted_designs(
        self,
        design_path: str,
        output_path: str,
        design_formats: list[dict],
    ):
        designs = self._load_images(design_path)

        for design, design_name in designs:
            logging.info("Start design generation: %s", design_name)
            new_formats_path = os.path.join(output_path, design_name, "images")
            os.makedirs(new_formats_path, exist_ok=True)
            for design_format in design_formats:
                x_inch = design_format["size_inch"][0]
                y_inch = design_format["size_inch"][1]
                formatted_image_filename = f"{design_name}-{x_inch}-{y_inch}.png"

                logging.info(" Formatting image: %s", formatted_image_filename)

                formatted_image = self.format_design(
                    design,
                    (x_inch, y_inch),
                    design_format["pixels_per_inch"],
                )

                formatted_image_path = os.path.join(
                    new_formats_path,
                    formatted_image_filename,
                )

                formatted_image.save(formatted_image_path)

    def format_design(
        self,
        image: Image.Image,
        inch_format: tuple[int, int],
        ppi: int,
    ) -> Image.Image:
        """Format the given image to the given format."""
        size_x, size_y = inch_format
        size_in_pixels = (size_x * ppi, size_y * ppi)
        formatted_image = self.resize_and_crop(image, *size_in_pixels)
        return formatted_image

    def resize_and_crop(
        self,
        image: Image.Image,
        size_x: int,
        size_y: int,
    ) -> Image.Image:
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

    @staticmethod
    def _load_images(path: str):
        """Load all PNG images in a folder or return single image"""
        images = []
        if os.path.isfile(path) and path.endswith(".png"):
            _, design_name = FormattedImageGenerator.extract_filename(path)
            images.append(
                (Image.open(path), design_name),
            )
        elif os.path.isdir(path):
            for file_name in os.listdir(path):
                if file_name.endswith(".png"):
                    file_path = os.path.join(path, file_name)
                    _, design_name = FormattedImageGenerator.extract_filename(file_path)
                    images.append(
                        (Image.open(file_path), design_name),
                    )
        else:
            raise ValueError("Invalid path specified")
        return images

    @staticmethod
    def extract_filename(path: str) -> tuple[str, str]:
        """
        Extracts the filename and filename without extension
        from a given path and returns them as a tuple
        """
        filename = os.path.basename(path)
        filename_without_extension = os.path.splitext(filename)[0]
        return (filename, filename_without_extension)
