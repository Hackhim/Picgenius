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


from dataclasses import dataclass, field
from typing import Optional, ClassVar

from PIL import Image

from picgenius import utils
from .watermark import Watermark


@dataclass
class TemplateElement:
    """Template element data."""

    position: tuple[int, int] | tuple[
        tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
    ]
    size: Optional[tuple[int, int]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    ratio: Optional[tuple[int, int]] = None
    zoom: Optional[float] = None
    zoom_position: Optional[tuple[int, int]] = None
    overlay: Optional[tuple[int, int, int, int]] = None
    transparency: Optional[float] = None

    def __post_init__(self):
        if self.overlay is not None:
            self.overlay = tuple(self.overlay)
        if self.ratio is not None:
            self.ratio = tuple(self.ratio)

        if self.transparency is not None:
            assert 0 <= self.transparency <= 1, "transparency must be between 0 and 1"


@dataclass
class TemplateImageElement:
    """Template image element data."""

    path: str
    position: tuple[int | str, int | str] = ("center", "center")
    width: Optional[str | int] = None
    height: Optional[str | int] = None
    margin: int = 0
    transparency: float = 1.0

    AVAILABLE_X_POS: ClassVar[list[str]] = ["left", "center", "right"]
    AVAILABLE_Y_POS: ClassVar[list[str]] = ["top", "center", "bottom"]

    def __post_init__(self):
        self.position = tuple(self.position)

        if isinstance(self.position[0], str):
            assert (
                self.position[0] in self.AVAILABLE_X_POS
            ), f"Position {self.position[0]} is not available."
        if isinstance(self.position[1], str):
            assert (
                self.position[1] in self.AVAILABLE_Y_POS
            ), f"Position {self.position[1]} is not available."

    def load_image(self):
        """Return image as PIL.Image."""
        return Image.open(self.path)


@dataclass
class Template:
    """Template data."""

    elements: list[TemplateElement]
    name: str = field(init=False)
    size: tuple[int, int] = (2000, 2000)
    background_color: tuple[int, int, int] = (0, 0, 0)
    path: Optional[str] = None
    filename: Optional[str] = None
    watermarks: list[Watermark] = field(default_factory=list)
    images: list[TemplateImageElement] = field(default_factory=list)
    repeat: bool = False

    def __post_init__(self):
        if self.filename is not None:
            _, name = utils.extract_filename(self.filename)
            self.name = name
        elif self.path is not None:
            filename, name = utils.extract_filename(self.path)
            self.name = name
            self.filename = filename
        else:
            raise ValueError("Either filename or path must be defined.")

        self.background_color = tuple(self.background_color)
