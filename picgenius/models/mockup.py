"""Module for Mockup class declaration."""
from typing import Optional, Generator
from moviepy.editor import ImageSequenceClip
import numpy as np
from .template import Template
from .watermark import Watermark
from .video_settings import Video
from .design import Design


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
        self.design_index = 0
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
            if watermark is not None and watermark not in self.watermarks:
                raise ValueError(f"Watermark {watermark} was not found.")

            watermark_kwarg = {}
            if self.watermarks is not None and watermark is not None:
                watermark_kwarg["watermark"] = self.watermarks[watermark]

            elements = template.get("elements", [])
            template_path = template.get("template_path", "")
            templates.append(Template(template_path, elements, **watermark_kwarg))
        return templates

    def _init_video(self, config_video: dict) -> Video:
        watermark = config_video.get("watermark")
        if watermark is not None:

        return Video(**config_video)


    def generate_templates(self, designs: list[Design]) -> Generator:
        """Generate all templates for a list of designs."""
        assert len(designs) == self.designs_count

        self.design_index = 0
        for template in self.templates:
            next_designs = self.get_next_designs(designs, template.count_elements)
            yield (template.generate_template(next_designs), template.name)

    def get_next_designs(self, designs: list[Design], n_designs: int) -> list[Design]:
        """Returns the next n designs starting from self.design_index."""
        assert n_designs > 0
        next_designs = []
        for _ in range(n_designs):
            next_designs.append(designs[self.design_index])
            self.design_index = (self.design_index + 1) % self.designs_count
        return next_designs

    def generate_video(self, design: Design) -> ImageSequenceClip:
        """"""
        # TODO: make video generation
