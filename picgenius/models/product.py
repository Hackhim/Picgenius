"""Module for Product class declaration."""

from dataclasses import dataclass

from .product_type import ProductType


@dataclass
class Design:
    """Design has the responsibility to generate its formatted images."""

    design_path: str
    name: str = ""


@dataclass
class Product:
    """Product's concern is to be the root of generating its visuals and formatted designs."""

    design_path: str
    type: ProductType
    name: str = ""
    designs: list[Design] = []

    # TODO: get the product name from design_path
    # TODO: create designs
    # TODO: check that design_path accords to product_type (design count)
    # TODO: create generation function
