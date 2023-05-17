"""Module"""

import yaml

from picgenius.models import (
    Format,
    Watermark,
    Template,
    TemplateElement,
    TemplateImageElement,
    VideoSettings,
    ProductType,
    Textbox,
)


class ConfigLoader:
    """Load the given config file."""

    file_path: str
    global_config: dict
    product_types: dict[str, ProductType]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.global_config = {}
        self.product_types = {}

    def load(self) -> dict[str, ProductType]:
        """Instanciate all the product types from the config file."""
        with open(self.file_path, "r", encoding="ascii") as config_file:
            config_data = yaml.safe_load(config_file)

        global_data = config_data.get("global", {})
        self._load_global(global_data)

        product_types_data = config_data.get("product_types", {})
        for product_type_name, product_type_data in product_types_data.items():
            self.product_types[product_type_name] = self._create_product_type(
                product_type_data
            )

        return self.product_types

    def _load_global(self, global_data: dict):
        formats_data = global_data.get("formats")
        if formats_data is not None:
            self.global_config["formats"] = [
                self._create_format(data) for data in formats_data
            ]

        watermarks_data = global_data.get("watermarks")
        if watermarks_data is not None:
            self.global_config["watermarks"] = {
                key: self._create_watermark(data)
                for key, data in watermarks_data.items()
            }

    def _create_product_type(self, product_type_data: dict) -> ProductType:
        formats = self._create_formats_from_product_type(product_type_data)
        watermarks = self._create_watermarks_from_product_type(product_type_data)
        video_settings = self._create_video_settings_from_product_type(
            product_type_data, watermarks
        )
        templates = self._create_templates_from_product_type(
            product_type_data, watermarks
        )

        product_type = ProductType(
            designs_count=product_type_data["designs-count"],
            templates=templates,
            formats=formats,
            watermarks=watermarks,
            video_settings=video_settings,
        )

        return product_type

    def _create_formats_from_product_type(
        self, product_type_data: dict
    ) -> list[Format]:
        formats_data = product_type_data.get("formats")
        if formats_data is not None:
            formats = [self._create_format(data) for data in formats_data]
        else:
            formats = self.global_config.get("formats", [])

        return formats

    def _create_format(self, format_data: dict) -> Format:
        return Format(**format_data)

    def _create_watermarks_from_product_type(
        self, product_type_data: dict
    ) -> dict[str, Watermark]:
        watermarks_data: dict = product_type_data.get("watermarks", {})
        return {
            key: self._create_watermark(data) for key, data in watermarks_data.items()
        }

    def _create_watermark(self, watermark_data: dict) -> Watermark:
        kwargs = {**watermark_data}
        textbox = watermark_data.get("textbox")
        if textbox is not None:
            textbox = Textbox(**textbox)
            kwargs["textbox"] = textbox
        return Watermark(**kwargs)

    def _create_video_settings_from_product_type(
        self, product_type_data: dict, watermarks: dict[str, Watermark]
    ) -> VideoSettings | None:
        video_settings_data = product_type_data.get("video")
        if not video_settings_data:
            return
        return self._create_video_settings(video_settings_data, watermarks)

    def _create_video_settings(
        self, video_settings_data: dict, watermarks: dict[str, Watermark]
    ) -> VideoSettings:
        kwargs = {**video_settings_data}
        watermarks_data = video_settings_data.get("watermarks", [])
        video_watermarks = [
            self._try_get_watermark(watermark_data, watermarks)
            for watermark_data in watermarks_data
        ]
        kwargs["watermarks"] = video_watermarks
        return VideoSettings(**kwargs)

    def _create_templates_from_product_type(
        self, product_type_data: dict, watermarks: dict[str, Watermark]
    ) -> list[Template]:
        templates_data = product_type_data.get("templates", [])
        return [
            self._create_template(template_data, watermarks)
            for template_data in templates_data
        ]

    def _create_template(
        self, template_data: dict, watermarks: dict[str, Watermark]
    ) -> Template:
        kwargs = {**template_data}
        kwargs["path"] = kwargs.pop("template_path")

        elements_data = template_data.get("elements", [])
        elements = [TemplateElement(**element_data) for element_data in elements_data]
        kwargs["elements"] = elements

        images_data = template_data.get("images", [])
        images = [TemplateImageElement(**image_data) for image_data in images_data]
        kwargs["images"] = images

        watermarks_data = template_data.get("watermarks", [])
        template_watermarks = [
            self._try_get_watermark(watermark_data, watermarks)
            for watermark_data in watermarks_data
        ]
        kwargs["watermarks"] = template_watermarks

        return Template(**kwargs)

    def _try_get_watermark(
        self, watermark_data: str | dict, watermarks: dict[str, Watermark]
    ) -> Watermark:
        """Return the watermark or raise exception if it doesn't exist."""
        watermark = None
        if isinstance(watermark_data, str):
            global_watermarks = self.global_config.get("watermarks", {})
            watermark = watermarks.get(
                watermark_data, global_watermarks.get(watermark_data)
            )
        elif isinstance(watermark_data, dict):
            watermark = self._create_watermark(watermark_data)

        if watermark is None:
            raise AttributeError(
                f"Watermark: {watermark_data} is invalid or not found."
            )

        return watermark
