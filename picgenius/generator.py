"""Module for PicGenerator class declaration."""
import logging
import os
import sys
from typing import Iterable

import yaml
from PIL import Image
from jsonschema import validate


from . import utils

CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "formats": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ppi", "inches"],
                "properties": {
                    "ppi": {
                        "type": "number",
                    },
                    "inches": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                    },
                },
            },
        },
        "mockups": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["designs-count", "templates"],
                "properties": {
                    "designs-count": {"type": "number"},
                    "templates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["template_path", "elements"],
                            "properties": {
                                "template_path": {"type": "string"},
                                "elements": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["position", "size"],
                                        "properties": {
                                            "position": {
                                                "type": "array",
                                                "items": {"type": "number"},
                                                "minItems": 2,
                                                "maxItems": 2,
                                            },
                                            "size": {
                                                "type": "array",
                                                "items": {"type": "number"},
                                                "minItems": 2,
                                                "maxItems": 2,
                                            },
                                        },
                                    },
                                },
                                "watermark": {"type": "string"},
                            },
                        },
                    },
                    "watermarks": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "font_path",
                                "text",
                            ],
                            "properties": {
                                "font_path": {"type": "string"},
                                "text": {"type": "string"},
                                "color": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 4,
                                    "maxItems": 4,
                                },
                                "position": {
                                    "type": "array",
                                    "items": {"type": ["string", "number"]},
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                                "margin": {"type": "number"},
                                "width": {"type": ["string", "number"]},
                                "textbox": {
                                    "type": "object",
                                    "required": ["padding", "color"],
                                    "properties": {
                                        "padding": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "minItems": 4,
                                            "maxItems": 4,
                                        },
                                        "color": {
                                            "type": "array",
                                            "items": {"type": "number"},
                                            "minItems": 4,
                                            "maxItems": 4,
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "video": {
                        "type": "object",
                        "properties": {
                            "movement": {"type": "string"},
                            "start_zoom": {"type": "string"},
                            "step": {"type": "number"},
                            "frames": {"type": "number"},
                            "fps": {"type": "number"},
                            "watermark": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
    "required": ["formats", "mockups"],
}


class PicGenerator:

    """
    PicGenerator has the responsibility to generate the product image(s), the mockup(s)
    and the video(s) specified in the config file for the specified design(s).
    """

    def __init__(self, config_path: str) -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            config: dict = yaml.safe_load(f)

        validate(config, CONFIG_SCHEMA)

        self.formats = config.get("formats", [])
        self.mockups = self._load_mockups_from_config(config)

    def _load_mockups_from_config(self, config: dict) -> dict[str, Mockup]:
        mockups = {}
        config_mockups = config.get("mockups", {})

        for mockup_name, config_mockup in config_mockups.items():
            mockups[mockup_name] = self._init_mockup_from_config(config_mockup)

        return mockups

    def _init_mockup_from_config(self, config_mockup: dict) -> Mockup:
        designs_count = config_mockup.get("designs-count", 0)
        templates = config_mockup.get("templates", [])
        watermarks = config_mockup.get("watermarks", None)
        video = config_mockup.get("video", None)
        mockup = Mockup(designs_count, templates, watermarks=watermarks, video=video)
        return mockup

    def generate_formatted_designs(self, design_path, output_dir: str):
        """Generate all formats for design."""
        designs = self.load_designs(design_path)

        for design in designs:
            logging.info("Start design generation: %s", design.name)
            images_dir = self.create_formatted_designs_dir(output_dir, design.name)
            for formatted_design, inches in design.generate_formats(self.formats):
                logging.info(" %sx%s", inches[0], inches[1])
                self.save_formatted_design(
                    formatted_design, images_dir, design.name, inches
                )

    def load_designs(self, path: str) -> list[Design]:
        """Returns a list of designs loaded from path."""
        return [Design(image, name) for image, name in utils.load_images(path)]

    def create_formatted_designs_dir(self, output_dir: str, design_name: str) -> str:
        """Create the output directory for formatted designs."""
        images_dir = os.path.join(output_dir, design_name, "images")
        os.makedirs(images_dir, exist_ok=True)
        return images_dir

    def save_formatted_design(
        self, image: Image.Image, output_dir: str, name: str, inches: tuple[int, int]
    ) -> None:
        """Save the formatted design into the output_dir."""
        formatted_image_filename = f"{name}-{inches[0]}-{inches[1]}.png"
        formatted_image_path = os.path.join(
            output_dir,
            formatted_image_filename,
        )
        image.save(formatted_image_path)

    def generate_mockup_templates(
        self, mockup_name: str, design_path: str, output_dir: str
    ) -> None:
        """Generate all templates of a mockup."""
        if mockup_name not in self.mockups:
            logging.error("Mockup %s mockup_name} not found.", mockup_name)
            sys.exit(-1)

        mockup = self.mockups[mockup_name]

        valid_paths = self._get_valid_design_paths(mockup, design_path)
        for designs_path in valid_paths:
            _, name = utils.extract_filename(designs_path)
            mockup_dir = os.path.join(output_dir, name, "mockups")

            designs = self.load_designs(designs_path)
            templates = mockup.generate_templates(designs)
            self._save_templates(templates, mockup_dir)

    def _get_valid_design_paths(self, mockup: Mockup, design_path: str) -> list[str]:
        """"""
        valid_paths = []
        if mockup.designs_count == 1:
            valid_paths.extend(self._get_paths_of_png_files(design_path))
        else:
            valid_paths.extend(
                self._get_paths_of_dirs_containing_n_png_files(
                    design_path, mockup.designs_count
                )
            )
        return valid_paths

    def _get_paths_of_png_files(self, design_path: str) -> list[str]:
        """Returns a list of paths to png files."""
        paths = []

        is_png_file = os.path.isfile(design_path) and design_path.endswith(".png")
        if is_png_file:
            paths.append(design_path)
        else:
            paths.extend(
                [
                    os.path.join(design_path, filename)
                    for filename in os.listdir(design_path)
                    if filename.endswith(".png")
                ]
            )

        return paths

    def _get_paths_of_dirs_containing_n_png_files(
        self, design_path: str, png_count: int
    ):
        paths = []

        if not os.path.isdir(design_path):
            return paths

        if self._check_path_is_directory_with_n_png_files(design_path, png_count):
            paths.append(design_path)
        else:
            directories = [
                os.path.join(design_path, dir)
                for dir in os.listdir(design_path)
                if os.path.isdir(os.path.join(design_path, dir))
            ]
            paths.extend(
                [
                    directory
                    for directory in directories
                    if self._check_path_is_directory_with_n_png_files(
                        os.path.join(directory), png_count
                    )
                ]
            )

        return paths

    def _check_path_is_directory_with_n_png_files(self, path: str, count: int) -> bool:
        return (
            os.path.isdir(path)
            and len([f for f in os.listdir(path) if f.endswith(".png")]) == count
        )

    def _save_templates(self, templates: Iterable, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        for template, name in templates:
            template_path = os.path.join(output_dir, name + ".png")
            template.save(template_path)
