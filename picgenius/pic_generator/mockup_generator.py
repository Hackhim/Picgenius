"""Module for MockupGenerator class definition."""
import os
import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import numpy as np

from . import utils
from . import image_processing as im


class Defaults:
    WATERMARKING_WIDTH = "70%"


class MockupGenerator:
    """Class that handle Mockup Generating."""

    def __init__(self, design_path: str, output_path: str, config: dict) -> None:
        self.design_path = design_path
        self.output_path = output_path
        self.config = config
        self.designs_count = self.config["designs_count"]
        self.is_set_of_designs = self.designs_count > 1
        self._validate_config_and_path()
        self.input_design_paths = self._list_design_paths()

    def _validate_config_and_path(self):
        """Check that the give paths and the config are valid."""

        if os.path.exists(self.output_path) and not os.path.isdir(self.output_path):
            raise AttributeError("Output path must be a folder.")
        elif not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)

        # check if the given design_path accords to the config
        if self.is_set_of_designs:
            self.has_almost_one_valid_dir = (
                self._check_almost_one_directory_with_count_designs(
                    self.design_path, self.designs_count
                )
            )
            self.is_valid_dir = self._check_path_is_directory_with_count_designs(
                self.design_path, self.designs_count
            )

            if not self.has_almost_one_valid_dir and not self.is_valid_dir:
                raise AttributeError(
                    "Designs path is not valid or png files not found."
                )
        else:
            self.is_png_file = self._check_path_is_png_file(self.design_path)
            self.has_almost_one_png_file = self._check_almost_one_png_file(
                self.design_path
            )

            if not self.has_almost_one_png_file and not self.is_png_file:
                raise AttributeError(
                    "Designs path must be a png file or a directory containing png files."
                )

    def _check_almost_one_directory_with_count_designs(
        self, path: str, count: int
    ) -> bool:
        return len(self._get_valid_directories_path(path, count)) > 0

    def _get_valid_directories_path(self, path: str, count: int) -> list[str]:
        directories = [
            os.path.join(path, dir) for dir in os.listdir(path) if os.path.isdir(dir)
        ]
        valid_directories = [
            directory
            for directory in directories
            if self._check_path_is_directory_with_count_designs(path, count)
        ]
        return valid_directories

    def _check_path_is_directory_with_count_designs(
        self, path: str, count: int
    ) -> bool:
        return (
            os.path.isdir(path)
            and len([f for f in os.listdir(path) if f.endswith(".png")]) == count
        )

    def _check_path_is_png_file(self, path: str) -> bool:
        return os.path.exists(path) and os.path.isfile(path) and path.endswith(".png")

    def _check_almost_one_png_file(self, path: str) -> bool:
        for filename in os.listdir(path):
            if filename.endswith(".png"):
                return True
        return False

    def _list_design_paths(self) -> list[str]:

        if self.is_set_of_designs:
            if self.is_valid_dir:
                return [self.design_path]
            else:
                return self._get_valid_directories_path(
                    self.design_path, self.designs_count
                )
        else:
            if self.is_png_file:
                return [self.design_path]
            else:
                return [
                    os.path.join(self.design_path, filename)
                    for filename in os.listdir(self.design_path)
                    if filename.endswith(".png")
                ]

    def generate(self):
        """Entry point of the generator to generate mockups for the specified config and design."""

        logging.info("Found designs:")
        for design_path in self.input_design_paths:
            logging.info(" - %s", design_path)

        if self.is_set_of_designs:
            raise NotImplementedError("TODO: MultipleDesigns mockups.")  # TODO
        else:
            self.generate_mockups_one_design_count()

    def generate_mockups_one_design_count(self):
        """Generates mockups for one specified design or for all designs in the folder."""

        for design_path in self.input_design_paths:
            designs = utils.load_images(design_path)
            for design, name in designs:
                self.generate_mockups_for_one_design(design, name)

    def generate_mockups_for_one_design(
        self,
        design: Image.Image,
        design_name: str,
        # mockups_path: str,
        # template_conf: dict,
    ):
        """Generate mockups based on a single design image and a template configuration."""
        logging.info("Start mockups generation for: %s", design_name)

        mockups_dir_path = os.path.join(self.output_path, design_name, "mockups")
        os.makedirs(mockups_dir_path, exist_ok=True)

        for template_metadata in self.config["templates"]:
            mockup_filename, _ = utils.extract_filename(
                template_metadata["template_path"]
            )
            mockup_path = os.path.join(mockups_dir_path, mockup_filename)
            mockup = self.generate_one_mockup_for_one_design(design, template_metadata)
            mockup.save(mockup_path)
            logging.info(" Generated: %s", mockup_path)

        # video_filename = "design_video.mp4"
        # logging.info(" Generating video: %s", video_filename)
        # self.generate_video(
        #    design,
        #    os.path.join(mockups_path, video_filename),
        #    watermarking=watermarking,
        # )

    def generate_one_mockup_for_one_design(
        self, design: Image.Image, template_metadata: dict
    ) -> Image.Image:
        """Generate a mockup image for the specified design and template metadata."""

        template_path = template_metadata["template_path"]
        design_position = template_metadata["position"]
        design_size = template_metadata["size"]

        template = Image.open(template_path)
        mockup = self.fit_design_in_template(
            template, design, design_position, design_size
        )
        mockup = self.apply_watermarking_on_image_if_needed(mockup, template_metadata)
        return mockup

    def fit_design_in_template(
        self,
        template: Image.Image,
        design: Image.Image,
        position: tuple[int, int],
        size: tuple[int, int],
    ) -> Image.Image:
        """Paste the specified design on the specified template."""
        resized_design = im.resize_and_crop(design, *size)
        template.paste(resized_design, position)
        return template

    def apply_watermarking_on_image_if_needed(
        self, image: Image.Image, template_metadata: dict
    ) -> Image.Image:
        """Apply specified or default watermarking if wanted."""

        watermarking = template_metadata.get("watermarking")
        watermarked = image

        if isinstance(watermarking, str):
            watermarking = self.config["watermarkings"][watermarking]

        if watermarking is not None:
            watermarked = self.apply_watermarking_on_image(image, watermarking)

        return watermarked

    def apply_watermarking_on_image(
        self, image: Image.Image, watermarking: dict
    ) -> Image.Image:
        """Read and applies the watermarking on the image."""

        print(watermarking)
        text = watermarking["text"]
        color = tuple(watermarking["color"])
        font_path = watermarking["font_path"]
        margin = watermarking.get("margin", 0)

        width = self.get_width_from_watermarking(image.width, watermarking)
        font = im.find_font_size(text, font_path, width)
        textbox = watermarking.get("textbox")
        textbox_kwargs = {}
        if textbox is not None:
            textbox_color = tuple(textbox.get("color"))
            textbox_padding = textbox.get("padding")
            textbox_padding = (
                tuple(textbox_padding)
                if isinstance(textbox_padding, list)
                else textbox_padding
            )
            textbox_kwargs["textbox_color"] = textbox_color
            textbox_kwargs["textbox_padding"] = textbox_padding

        text_position = self.get_text_position_from_watermarking(
            image.size, font.getsize(text), watermarking, margin=margin
        )

        watermarked = im.paste_text_on_image(
            image, text, font, text_position, color=color, **textbox_kwargs
        )
        return watermarked

    def get_width_from_watermarking(self, image_width: int, watermarking: dict) -> int:
        """Returns the width of the text in pixels from watermarking infos."""
        width_arg = watermarking.get("width", Defaults.WATERMARKING_WIDTH)
        if isinstance(width_arg, str) and width_arg.endswith("%"):
            percentage = int(width_arg.strip("%")) / 100
            width = int(image_width * percentage)
        else:
            width = int(width_arg)
        return width

    def get_text_position_from_watermarking(
        self, image_size: tuple, text_size: tuple, watermarking: dict, margin: int = 0
    ) -> tuple[int, int]:
        """Returns the position X Y where to place the text from watermarking infos."""
        available_x_pos = ["left", "center", "right"]
        available_y_pos = ["top", "center", "bottom"]

        x_pos = watermarking["x_pos"]
        y_pos = watermarking["y_pos"]

        if isinstance(x_pos, str) and x_pos in available_x_pos:
            if x_pos == "center":
                x_pos = (image_size[0] - text_size[0]) // 2
            elif x_pos == "right":
                x_pos = image_size[0] - text_size[0] - margin
            else:
                x_pos = 0 + margin
        else:
            x_pos = int(x_pos)

        if isinstance(y_pos, str) and y_pos in available_y_pos:
            if y_pos == "center":
                y_pos = (image_size[1] - text_size[1]) // 2
            elif y_pos == "bottom":
                y_pos = image_size[1] - text_size[1] - margin
            else:
                y_pos = 0 + margin
        else:
            y_pos = int(y_pos)

        return (x_pos, y_pos)


#
#    def generate_video(
#        self, image: Image.Image, video_path: str, watermarking: Optional[dict] = None
#    ):
#        """Generate a zooming video into the design (mp4)."""
#        # TODO: Handle video generation with different variants
#        image = self.resize_and_crop(image, 2000, 2000)
#        if watermarking is not None:
#            image = self.apply_watermarking(image.convert("RGBA"), watermarking)
#
#        frames = self.generate_video_frames(image)
#        np_frames = [np.array(img) for img in frames]
#        clip = ImageSequenceClip(np_frames, fps=20)
#        clip.write_videofile(video_path, verbose=False, logger=None)
