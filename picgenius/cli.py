"""Entry point to use the picgenius cli tool."""
import json
import logging
from typing import Optional
import click

# from pic_generator import MockupGenerator, FormattedImageGenerator
from pic_generator import PicGenerator


@click.group
@click.option("--config", "-f", "config_path", default="./picgenius.yml", type=str)
@click.option("--debug", is_flag=True)
@click.pass_context
def picgenius(ctx, config_path: str, debug: bool):
    """Root group for pic genius commands."""
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

    if debug:
        logging.getLogger().setLevel("DEBUG")

    ctx.obj = PicGenerator(config_path=config_path)


@picgenius.command
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
    help="Path to output directory product images.",
)
@click.pass_obj
def format_design(picgenerator: PicGenerator, design_path: str, output_dir: str):
    """Format specified design(s) to the specified formats in the config file."""
    picgenerator.generate_formatted_designs(design_path, output_dir)


@picgenius.command
@click.option(
    "--mockup",
    "-m",
    "mockup_name",
    type=str,
    required=True,
    help="Template name to use, template should be defined in the config file.",
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
    help="Path to output product images.",
)
@click.pass_obj
def generate_mockups(
    picgenerator: PicGenerator, mockup_name: str, design_path: str, output_dir: str
):
    """Generate mockups for specified designs, using specified template."""
    picgenerator.generate_mockup_templates(mockup_name, design_path, output_dir)
