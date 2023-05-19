"""Module for Product class declaration."""
from dataclasses import dataclass, field

from PIL import Image

from picgenius import utils
from .product_type import ProductType


@dataclass
class Design:
    """Design has the responsibility to generate its formatted images."""

    path: str
    name: str = ""

    def __post_init__(self):
        _, name = utils.extract_filename(self.path)
        self.name = name

    def load_image(self) -> Image.Image:
        """Loads the image."""
        return Image.open(self.path)


@dataclass
class Product:
    """Product's concern is to be the root of generating its visuals and formatted designs."""

    type: ProductType
    design_path: str
    name: str = field(init=False)
    designs: list[Design] = field(init=False)

    def __post_init__(self):
        self.design_path = self.design_path.strip("/")
        _, name = utils.extract_filename(self.design_path)
        self.name = name
        self.designs = []
        for design_path in utils.find_image_file_paths(self.design_path):
            self.designs.append(Design(design_path))

        if len(self.designs) != self.type.designs_count:
            raise AttributeError(
                "The number of product designs doesn't match the product type count: "
                f"{len(self.designs)} != {self.type.designs_count}"
            )
