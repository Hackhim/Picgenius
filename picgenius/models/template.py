"""Module for Template class declaration."""
# import os
# from typing import Optional
#
# from PIL import Image
#
# from .watermark import Watermark
# from .design import Design
# from . import processing as im
# from . import utils


from dataclasses import dataclass
from typing import Optional

from picgenius import utils
from .watermark import Watermark


@dataclass
class TemplateElement:
    """Template element data."""

    position: tuple[int, int] | tuple[
        tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
    ]
    size: Optional[tuple[int, int]] = None
    overlay: Optional[tuple[int, int, int, int]] = None

    def __post_init__(self):
        if self.overlay is not None:
            self.overlay = tuple(self.overlay)


@dataclass
class Template:
    """Template data."""

    elements: list[TemplateElement]
    path: str
    name: str = ""
    watermark: Optional[Watermark] = None

    def __post_init__(self):
        _, name = utils.extract_filename(self.path)
        self.name = name
