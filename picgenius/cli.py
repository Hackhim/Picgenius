"""Entry point to use the picgenius cli tool."""
import click


@click.group
def picgenius():
    """Root group for pic genius commands."""


@picgenius.command
def format_designs():
    """Format specified design(s) to the specified formats."""
    print("Formatting images")
