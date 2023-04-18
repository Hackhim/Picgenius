"""Entry point to use the picgenius cli tool."""
import logging
from dataclasses import dataclass, field

import click

from picgenius.config import ConfigLoader
from picgenius.models import Product, ProductType
from picgenius.renderers import ProductRenderer


@dataclass
class ContextObject:
    """Context object to pass between commands."""

    config: ConfigLoader
    product_types: dict[str, ProductType]
    selected_product_type: ProductType = field(init=False)
    design_path: str = field(init=False)
    output_dir: str = field(init=False)


@click.group
@click.option("--config", "-f", "config_path", default="./picgenius.yml", type=str)
@click.option("--debug", is_flag=True)
@click.pass_context
def picgenius(ctx, config_path: str, debug: bool):
    """Root group for pic genius commands."""
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

    if debug:
        logging.getLogger().setLevel("DEBUG")

    config_loader = ConfigLoader(config_path)
    context_object = ContextObject(config_loader, config_loader.load())
    ctx.obj = context_object


@picgenius.group
@click.option(
    "--product-type",
    "-p",
    "product_type_name",
    type=str,
    required=True,
    help="Product type to use, product type must be defined in the config file.",
)
@click.option(
    "--design",
    "-d",
    "design_path",
    default="./workdir/designs",
    help="Path to designs folder or design file.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    default="./workdir/products",
    help="Output directory.",
)
@click.pass_obj
def generate(
    context_object: ContextObject,
    product_type_name: str,
    design_path: str,
    output_dir: str,
):
    """Generate selected medias."""
    product_type = context_object.product_types.get(product_type_name)
    if product_type is None:
        raise ValueError(f'Product type "{product_type_name}" doesn\'t exist.')

    context_object.selected_product_type = product_type
    context_object.design_path = design_path
    context_object.output_dir = output_dir


@generate.command
@click.pass_obj
def all_medias(context_object: ContextObject):
    """Generate all medias of product type."""

    product = Product(context_object.selected_product_type, context_object.design_path)
    ProductRenderer.generate_product_templates(product, context_object.output_dir)
