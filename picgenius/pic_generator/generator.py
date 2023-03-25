"""Module for PicGenerator class declaration."""
import yaml
from jsonschema import validate
from .mockup import Mockup

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

    def _load_mockups_from_config(self, config: dict) -> dict:
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
