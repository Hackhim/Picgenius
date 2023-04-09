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

from .watermark import Watermark


@dataclass
class TemplateElement:
    """Template element data."""

    position: tuple[int, int]
    size: tuple[int, int]


@dataclass
class Template:
    """Template data."""

    path: str
    elements: list[TemplateElement]
    watermark: Optional[Watermark] = None
