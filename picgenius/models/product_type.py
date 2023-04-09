"""Module for ProductType class declaration."""

from dataclasses import dataclass
from typing import Optional

from .template import Template
from .watermark import Watermark
from .video_settings import VideoSettings


@dataclass
class Format:
    """Format data."""

    ppi: int
    inches: int


@dataclass
class ProductType:
    """
    ProductType has the concern to be the root of a product visuals,
    and launch the generation of it.
    """

    designs_count: int
    templates: list[Template]
    watermarks: Optional[list[Watermark]] = None
    video_settings: Optional[VideoSettings] = None
