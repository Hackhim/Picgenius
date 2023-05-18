"""Module for Controller class declaration."""
import os
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from picgenius.models import ProductType, Product, Design
from picgenius.renderers import ProductRenderer, DesignRenderer
from picgenius.logger import PicGeniusLogger
from picgenius import utils


class Controller:
    """Its responsibility is to call the different renderers, with according attributes."""

    design_path: str
    product_type: Optional[ProductType]
    products: list[Product]

    def __init__(
        self, design_path: str, product_type: Optional[ProductType] = None
    ) -> None:
        self.design_path = design_path
        self.product_type = product_type
        if product_type is None:
            self.products = []
        else:
            self.products = Controller.create_products(product_type, design_path)
        self.logger = PicGeniusLogger()

    @staticmethod
    def create_products(product_type: ProductType, design_path: str) -> list[Product]:
        """Instanciate all products according to the given type and path."""

        designs_count = product_type.designs_count
        return [
            Product(product_type, product_path)
            for product_path in utils.find_product_paths(designs_count, design_path)
        ]

    def generate_products_all_assets(self, output_dir: str, max_threads: int = 4):
        """Create products from design_path, then generate all assets"""

        with ThreadPoolExecutor(max_threads) as executor:
            futures_to_products = {
                executor.submit(
                    self.process_product_generation, product, output_dir
                ): product
                for product in self.products
            }

            for future in as_completed(futures_to_products):
                future.result()

    def process_product_generation(self, product: Product, output_dir: str):
        """Process the generation of all assets for the given product."""

        self.logger.info("(%s) Start product all assets generation", product.name)
        self.logger.info(
            "(%s) output directory: %s",
            product.name,
            os.path.join(output_dir, product.name),
        )
        count_formats = len(product.type.formats)
        count_templates = len(product.type.templates)
        ProductRenderer.generate_formatted_designs(
            product, output_dir, max_threads=count_formats
        )
        ProductRenderer.generate_templates(
            product, output_dir, max_threads=count_templates
        )
        ProductRenderer.generate_video(product, output_dir)
        self.logger.info("(%s) All assets generation done", product.name)
        self.logger.info("")

    def generate_products_templates(
        self, output_dir: str, template_name: Optional[str] = None
    ):
        """Generate products templates."""
        # TODO: Add generation of specified template
        self.log_found_products(self.products)
        for product in self.products:
            self.logger.info("(%s) Start templates generation", product.name)
            self.logger.info(
                "(%s) output directory: %s",
                product.name,
                os.path.join(output_dir, product.name),
            )
            ProductRenderer.generate_templates(product, output_dir)
            self.logger.info("(%s) Templates generation done", product.name)
            self.logger.info("")

    def generate_products_video(self, output_dir: str):
        """Generate products video."""
        for product in self.products:
            self.logger.info("(%s) Start video generation", product.name)
            self.logger.info(
                "(%s) output directory: %s",
                product.name,
                os.path.join(output_dir, product.name),
            )
            ProductRenderer.generate_video(product, output_dir)
            self.logger.info("(%s) Video generation done", product.name)
            self.logger.info("")

    def generate_products_formatted_designs(self, output_dir: str):
        """Generate products formatted designs."""
        for product in self.products:
            self.logger.info("(%s) Start formatted designs generation", product.name)
            self.logger.info(
                "(%s) output directory: %s",
                product.name,
                os.path.join(output_dir, product.name),
            )
            ProductRenderer.generate_formatted_designs(product, output_dir)
            self.logger.info("(%s) Formatted designs generation done", product.name)
            self.logger.info("")

    # TODO: add design upscaling for given product
    # def generate_product_upscaled_designs(self, output_dir: str, scale: int):
    #    """Generate upscaled designs."""
    #    for product in self.products:
    #        self.logger.info(
    #            "(%s) Start x%d upscaled designs generation", product.name, scale
    #        )
    #        self.logger.info("(%s) output directory: %s", product.name, output_dir)
    #        ProductRenderer.generate_formatted_designs(product, output_dir)
    #        self.logger.info(
    #            "(%s) x%s upscaled designs generation done", product.name, scale
    #        )

    def upscale_designs(
        self,
        output_dir: str,
        scale: int,
        cpu: bool = False,
        suffix: Optional[str] = None,
        file_extension: str = "jpg",
    ):
        """Upscale designs found in design_path."""
        if suffix is None:
            suffix = f"-x{scale}-upscaled"

        designs = [
            Design(design_path)
            for design_path in utils.find_image_file_paths(self.design_path)
        ]
        os.makedirs(output_dir, exist_ok=True)

        self.log_found_designs(designs)
        for design in designs:
            upscaled_path = os.path.join(
                output_dir, f"{design.name}{suffix}.{file_extension}"
            )
            self.logger.info("(%s) Start x%d upscale", design.name, scale)
            self.logger.info("(%s) output: %s", design.name, upscaled_path)
            upscaled_design = DesignRenderer.upscale_design(design, scale, cpu=cpu)
            upscaled_design.save(upscaled_path)
            self.logger.info("(%s) x%s upscale done", design.name, scale)
            self.logger.info("")

    def log_found_designs(self, designs: list[Design]):
        """Log found designs."""
        self.logger.info("Found %d designs in %s", len(designs), self.design_path)
        for design in designs:
            self.logger.info("\t%s (%s)", design.path, design.name)
        self.logger.info("")

    def log_found_products(self, products: list[Product]):
        """Log found products."""
        self.logger.info("Found %d products in %s", len(products), self.design_path)
        for product in products:
            self.logger.info("(%s)", product.name)
            for design in product.designs:
                self.logger.info("\t%s", design.path)
            self.logger.info("")
