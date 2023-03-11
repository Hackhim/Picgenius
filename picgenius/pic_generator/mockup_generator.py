"""Module for MockupGenerator class definition."""
import os
import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import numpy as np


class MockupGenerator:
    """Class that handle Mockup Generating."""

    def generate_mockups(
        self, design_path: str, mockups_path: str, template_conf: dict
    ):
        """
        Generate mockups based on a design image and a template configuration.

        Raises:
            AttributeError: If the mockups_path specified is not a directory.
            NotImplementedError: If generating multiple designs is not yet supported.
        """
        if os.path.exists(mockups_path) and not os.path.isdir(mockups_path):
            raise AttributeError("mockup_path must be a folder.")

        multiple_designs: bool = int(template_conf["designs_count"]) > 1

        if multiple_designs:
            raise NotImplementedError("TODO: MultipleDesigns mockups.")
        else:
            self.generate_1_designs_mockups(design_path, mockups_path, template_conf)

    def generate_1_designs_mockups(
        self, design_path: str, mockups_path: str, template_conf: dict
    ):
        """Generates mockups for one specified design or for all designs in the folder."""
        designs = self._load_images(design_path)
        for design, name in designs:
            self.generate_mockups_for_design(design, name, mockups_path, template_conf)

    def generate_mockups_for_design(
        self,
        design: Image.Image,
        design_name: str,
        mockups_path: str,
        template_conf: dict,
    ):
        """Generate mockups based on a single design image and a template configuration."""
        new_mockup_path = os.path.join(mockups_path, design_name)
        os.makedirs(new_mockup_path, exist_ok=True)

        logging.info("Start design generation: %s", design_name)

        watermarking = template_conf.get("watermarking")

        video_filename = "design_video.mp4"
        logging.info(" Generating video: %s", video_filename)
        self.generate_video(
            design,
            os.path.join(new_mockup_path, video_filename),
            watermarking=watermarking,
        )

        for template_metadata in template_conf["templates"]:
            mockup_filename, _ = self.extract_filename(
                template_metadata["template_path"]
            )
            logging.info(" Generating mockup: %s", mockup_filename)

            mockup_path = os.path.join(new_mockup_path, mockup_filename)

            template = Image.open(template_metadata["template_path"])
            mockup = self.paste_image_on_template(
                template,
                design,
                template_metadata["position"],
                template_metadata["size"],
            )

            if watermarking is not None:
                mockup = self.apply_watermarking(mockup, watermarking)
            mockup.save(mockup_path)

    def generate_video(
        self, image: Image.Image, video_path: str, watermarking: Optional[dict] = None
    ):
        """Generate a zooming video into the design (mp4)."""
        image = self.resize_and_crop(image, 2000, 2000)
        if watermarking is not None:
            image = self.apply_watermarking(image.convert("RGBA"), watermarking)

        frames = self.generate_video_frames(image)
        np_frames = [np.array(img) for img in frames]
        clip = ImageSequenceClip(np_frames, fps=20)
        clip.write_videofile(video_path, verbose=False, logger=None)

    def generate_video_frames(self, image: Image.Image, frames: int = 100, step=1):
        """Generate the frames for the video."""
        images = []
        for i in range(0, frames, step):
            tl = i
            br = image.width - i

            zoom_region = (tl, tl, br, br)
            zoom_image = image.crop(zoom_region).resize(
                image.size, resample=Image.LANCZOS
            )
            images.append(zoom_image)
        return images

    def paste_image_on_template(
        self,
        template: Image.Image,
        image: Image.Image,
        position: tuple[int, int],
        size: tuple[int, int],
    ):
        """Paste the specified image on the specified template."""
        resized_design = self.resize_and_crop(image, *size)
        template.paste(resized_design, position)
        return template

    def resize_and_crop(self, image: Image.Image, size_x: int, size_y: int):
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

    def apply_watermarking(self, image: Image.Image, watermarking: dict):
        """
        Applies watermarking to an image based on the provided dictionary.

        Args:
            image (PIL.Image.Image): The image to apply watermarking to.
            watermarking (dict): A dictionary containing watermarking parameters.

        Returns:
            PIL.Image.Image: The watermarked image.

        Raises:
            NotImplementedError: If the watermarking type is not supported.
        """
        if watermarking.get("type") == "text":
            font = self.get_watermarking_font(
                image,
                watermarking["text"],
                watermarking["font_path"],
                margin=watermarking["margin"],
            )
            watermarked = self.paste_text_on_image(
                image, watermarking["text"], font, tuple(watermarking["color"])
            )
        else:
            raise NotImplementedError("TODO: handle other type of watermarking.")

        return watermarked

    def get_watermarking_font(
        self, image: Image.Image, text: str, font_path: str, margin: int
    ):
        """
        Return a font object that can be used to apply watermarking text to an image.

        Args:
            image (PIL.Image.Image): The image to be watermarked.
            text (str): The text to be used as watermark.
            font_path (str): The path of the font file to be used for watermarking.
            margin (int): The margin size to be used when applying the watermark.

        Returns:
            PIL.ImageFont.FreeTypeFont: A font object that can be used to apply
            watermarking text to an image.
        """
        max_width = image.width - (margin * 2)
        font_size = 1
        font = ImageFont.truetype(font_path, font_size)
        while font.getlength(text) < max_width:
            font_size += 1
            font = ImageFont.truetype(font_path, font_size)
        return font

    def paste_text_on_image(
        self,
        image: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: tuple[int, int, int, int] = (0, 0, 0, 0),
    ):
        """
        Paste given text onto the given image using the specified font and color.

        Args:
            image (PIL.Image.Image): The image onto which to paste the text.
            text (str): The text to paste onto the image.
            font (PIL.ImageFont.FreeTypeFont): The font to use for the text.
            color (tuple[int, int, int, int], optional):
                The color of the text, as a tuple of RGBA values. Defaults to (0, 0, 0, 0).

        Returns:
            PIL.Image.Image: The resulting image with the text pasted onto it.
        """
        mask = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(mask)

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_position = (
            (image.width - text_bbox[2]) // 2,
            (image.height - text_bbox[3]) // 2,
        )

        draw.text(text_position, text, font=font, fill=color)
        combined = Image.alpha_composite(image, mask)
        return combined

    @staticmethod
    def _load_images(path: str):
        """Load all PNG images in a folder or return single image"""
        images = []
        if os.path.isfile(path) and path.endswith(".png"):
            _, design_name = MockupGenerator.extract_filename(path)
            images.append(
                (Image.open(path), design_name),
            )
        elif os.path.isdir(path):
            for file_name in os.listdir(path):
                if file_name.endswith(".png"):
                    file_path = os.path.join(path, file_name)
                    _, design_name = MockupGenerator.extract_filename(file_path)
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

    @staticmethod
    def ensure_path_exists(path):
        """Ensures that the given path exists by creating any missing directories."""
        os.makedirs(path, exist_ok=True)
