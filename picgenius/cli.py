"""Entry point to use the picgenius cli tool."""
from dataclasses import dataclass, field
from typing import Optional

import click

from .config import ConfigLoader
from .models import ProductType
from .controller import Controller
from .logger import PicGeniusLogger


@dataclass
class ContextObject:
    """Context object to pass between commands."""

    config: ConfigLoader
    product_types: dict[str, ProductType] = field(init=False)
    selected_product_type: ProductType = field(init=False)
    design_path: str = field(init=False)
    output_dir: str = field(init=False)

    def load_product_types(self):
        """Load product types from config file."""
        self.product_types = self.config.load()


@click.group
@click.option("--config", "-f", "config_path", default="./picgenius.yml", type=str)
@click.option("--debug", is_flag=True)
@click.pass_context
def picgenius(ctx, config_path: str, debug: bool):
    """Root group for pic genius commands."""
    logger = PicGeniusLogger()
    if debug:
        logger.setLevel("DEBUG")

    config_loader = ConfigLoader(config_path)
    context_object = ContextObject(config_loader)
    ctx.obj = context_object


@picgenius.group
@click.argument("product_type", type=str)
@click.argument("design_path", type=str)
@click.option(
    "--output",
    "-o",
    "output_dir",
    default="./products",
    help="Output directory. Default: ./products",
)
@click.pass_obj
def product(
    context_object: ContextObject,
    product_type: str,
    design_path: str,
    output_dir: str,
):
    """Generate specified product visuals."""
    context_object.load_product_types()

    selected_product_type = context_object.product_types.get(product_type)
    if selected_product_type is None:
        raise ValueError(f'Product type "{product_type}" doesn\'t exist.')

    context_object.selected_product_type = selected_product_type
    context_object.design_path = design_path
    context_object.output_dir = output_dir


@product.command
@click.pass_obj
def generate_all(context_object: ContextObject):
    """Generate all medias of product type."""

    product_type = context_object.selected_product_type
    design_path = context_object.design_path
    output_dir = context_object.output_dir

    controller = Controller(design_path, product_type=product_type)
    controller.generate_products_all_assets(output_dir)


@product.command
@click.option(
    "--template",
    "-t",
    "template_name",
    help="Optional template name.",
)
@click.pass_obj
def generate_templates(context_object: ContextObject, template_name: Optional[str]):
    """Generate templates of product type."""

    product_type = context_object.selected_product_type
    design_path = context_object.design_path
    output_dir = context_object.output_dir

    controller = Controller(design_path, product_type=product_type)
    controller.generate_products_templates(output_dir, template_name)


@product.command
@click.pass_obj
def generate_video(context_object: ContextObject):
    """Generate templates of product type."""

    product_type = context_object.selected_product_type
    design_path = context_object.design_path
    output_dir = context_object.output_dir

    controller = Controller(design_path, product_type=product_type)
    controller.generate_products_video(output_dir)


@product.command
@click.pass_obj
def format_designs(context_object: ContextObject):
    """Generate templates of product type."""

    product_type = context_object.selected_product_type
    design_path = context_object.design_path
    output_dir = context_object.output_dir

    controller = Controller(design_path, product_type=product_type)
    controller.generate_products_formatted_designs(output_dir)


@picgenius.command
@click.argument("design_path", type=str)
@click.option(
    "--output",
    "-o",
    "output_dir",
    default="./upscaled",
    help="Output directory. Default: ./upscaled",
)
@click.option(
    "--scale",
    "-s",
    "scale",
    type=int,
    default=2,
    help="Available scale multiplicators: 2, 4, 8, 10, 12 and 16. Default: 2",
)
@click.option(
    "--cpu",
    is_flag=True,
    type=bool,
    default=False,
    help="Force usage of CPU.",
)
def upscale(design_path: str, output_dir: str, scale: int, cpu: bool):
    """Upscale given design."""
    controller = Controller(design_path)
    controller.upscale_designs(output_dir, scale, cpu=cpu)
