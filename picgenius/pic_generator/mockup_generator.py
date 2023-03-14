"""Module for MockupGenerator class definition."""
import os
import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import numpy as np

import utils
import image_processing as im


class MockupGenerator:
    """Class that handle Mockup Generating."""

    def __init__(self, design_path: str, output_path: str, config: dict) -> None:
        self.design_path = design_path
        self.output_path = output_path
        self.config = config
        self.designs_count = self.config["designs_count"]
        self._validate_config_and_path()

    def _validate_config_and_path(self):
        """Check that the give paths and the config are valid."""

        if os.path.exists(self.output_path) and not os.path.isdir(self.output_path):
            raise AttributeError("mockup_path must be a folder.")
        elif not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)

        # check if the given design_path accords to the config
        if self.designs_count > 1:
            has_almost_one_valid_dir = (
                self._check_almost_one_directory_with_count_designs(
                    self.design_path, self.designs_count
                )
            )
            is_valid_dir = self._check_path_is_directory_with_count_designs(
                self.design_path, self.designs_count
            )

            if not has_almost_one_valid_dir and not is_valid_dir:
                raise AttributeError(
                    "Designs path is not valid or png files not found."
                )
        else:
            is_png_file = self._check_path_is_png_file(self.design_path)
            has_almost_one_png_file = self._check_almost_one_png_file(self.design_path)

            if not has_almost_one_png_file or not is_png_file:
                raise AttributeError(
                    "Designs path must be a png file or a directory containing png files."
                )

    def _check_almost_one_directory_with_count_designs(self, path, count: int) -> bool:
        directories = [
            os.path.join(path, dir) for dir in os.listdir(path) if os.path.isdir(dir)
        ]

        return any(
            self._check_path_is_directory_with_count_designs(directory, count)
            for directory in directories
        )

    def _check_path_is_directory_with_count_designs(
        self, path: str, count: int
    ) -> bool:
        return (
            os.path.isdir(path)
            and len([f for f in os.listdir(path) if f.endswith(".png")]) == count
        )

    def _check_path_is_png_file(self, path: str) -> bool:
        return os.path.exists(path) and os.path.isfile(path) and path.endswith(".png")

    def _check_almost_one_png_file(self, path) -> bool:
        for filename in os.listdir(path):
            if filename.endswith(".png"):
                return True
        return False

    def generate_mockups(
        self, design_path: str, mockups_path: str, template_conf: dict
    ):
        """Generate mockups based on a design image and a template configuration."""
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
        designs = utils.load_images(design_path)
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
        new_mockup_path = os.path.join(mockups_path, design_name, "mockups")
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
