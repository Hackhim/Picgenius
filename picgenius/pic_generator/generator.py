"""Module for PicGenerator class declaration."""
import yaml
from jsonschema import validate


class PicGenerator:

    """
    PicGenerator has the responsibility to generate the product image(s), the mockup(s)
    and the video(s) specified in the config file for the specified design(s).
    """

    config_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "formats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ppi": {
                            "type": "integer",
                        },
                        "inches": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2,
                        },
                    },
                },
            },
            "mockups": {},
        },
        "required": ["formats", "mockups"],
    }

    def __init__(self, config_path: str) -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            config: dict = yaml.safe_load(f)

        is_valid = validate(config, self.config_schema)
        print(is_valid)

        self.formats = self._load_formats_from_config(config)
        self.mockups = self._load_mockups_from_config(config)

    def _load_formats_from_config(self, config: dict) -> list[dict]:
        config_formats = config.get("formats", [])

        formats = []
        for format in config_formats:
            pass
        return formats

    def _load_mockups_from_config(self, config: dict) -> dict:
        return []
