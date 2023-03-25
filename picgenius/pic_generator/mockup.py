"""Module for Mockup class declaration."""
from typing import Optional
from .template import Template
from .watermark import Watermark
from .video import Video


class Mockup:
    """Mockup has the responsibility to generate the mockups related files."""

    def __init__(
        self,
        designs_count: int,
        templates: list[dict],
        watermarks: Optional[dict] = None,
        video: Optional[dict] = None,
    ) -> None:

        assert designs_count > 0
        self.designs_count = designs_count

        self.watermarks = (
            self._init_watermarks(watermarks) if watermarks is not None else None
        )
        self.templates = self._init_templates(templates)
        self.video = Video(**video) if video is not None else None

    def _init_watermarks(self, config_watermarks: dict) -> dict:
        watermarks = {}
        for name, watermark in config_watermarks.items():
            watermarks[name] = Watermark(**watermark)
        return watermarks

    def _init_templates(self, config_templates: list[dict]) -> list[Template]:

        templates = []
        for template in config_templates:
            watermark = template.get("watermark")

            if watermark is None or watermark not in self.watermarks:
                raise ValueError(f"Watermark {watermark} was not found.")

            elements = template.get("elements", [])
            template_path = template.get("template_path", "")
            templates.append(Template(template_path, elements, watermark=watermark))
        return templates
