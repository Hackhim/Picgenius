"""Entry point to use the picgenius cli tool."""
import json
import logging
from typing import Optional
import click

from pic_generator import MockupGenerator, FormattedImageGenerator


class Config:
    """Config class that stores templates data and design formats."""

    mockup_templates: dict = {}
    design_formats: list = []

    def __init__(
        self,
        config_json: Optional[dict] = None,
        config_path: Optional[str] = None,
    ) -> None:
        if config_json is None and config_path is None:
            raise AttributeError("Missing config_json or config_path attribute.")

        config = config_json or {}
        if config_json is None and config_path is not None:
            config = self._read_config_file(config_path)

        self._load_config_json(config)

    def _load_config_json(self, config_json: dict) -> None:
        self.mockup_templates = config_json.get("mockup_templates", {})
        self.design_formats = config_json.get("design_formats", [])

    def _read_config_file(self, config_path: str) -> dict:
        """Load the specified config file."""
        config_data = {}

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        return config_data


@click.group
@click.option("--config", "-f", "config_path", default="./picgenius.conf", type=str)
@click.option("--debug", is_flag=True)
@click.option("--quiet", is_flag=True)
@click.pass_context
def picgenius(ctx, config_path: str, debug: bool, quiet: bool):
    """Root group for pic genius commands."""
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

    if debug:
        logging.getLogger().setLevel("DEBUG")
    # TODO: add quiet logging

    ctx.obj = Config(config_path=config_path)


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
    "output_path",
    default="./workdir/mockups",
    help="Path to output mockups.",
)
@click.pass_obj
def format_design(config, design_path, output_path):
    """Format specified design(s) to the specified formats in the config file."""
    generator = FormattedImageGenerator()
    generator.generate_formatted_designs(
        design_path, output_path, config.design_formats
    )


@picgenius.command
@click.option(
    "--template",
    "-t",
    "template_name",
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
    "output_path",
    default="./workdir/mockups",
    help="Path to output mockups.",
)
@click.pass_obj
def generate_mockups(config, template_name, design_path, output_path):
    """Generate mockups for specified designs, using specified template."""

    if template_name not in config.mockup_templates:
        logging.error('Template name "%s" not found.', template_name)

    template_config = config.mockup_templates[template_name]

    generator = MockupGenerator()
    generator.generate_mockups(design_path, output_path, template_config)
