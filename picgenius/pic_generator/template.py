"""Module for Template class declaration."""
import os
from typing import Optional
from .watermark import Watermark


class Template:
    """
    Template has the responsibility to apply the given design(s) on the template,
    and apply watermark if needed.
    """

    def __init__(
        self,
        template_path: str,
        elements: list[dict],
        watermark: Optional[Watermark] = None,
    ) -> None:
        if not os.path.exists(template_path) or not os.path.isfile(template_path):
            raise ValueError("Incorrect template path.")

        self.elements = elements
        self.watermark = watermark
