"""Module for Controller class declaration."""
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from picgenius.models import ProductType, Product
from picgenius.renderers import ProductRenderer
from picgenius.logger import PicGeniusLogger
from picgenius import utils


class Controller:
    """Its responsibility is to call the different renderers, with according attributes."""

    design_path: str
    product_type: ProductType
    products: list[Product]

    def __init__(self, product_type: ProductType, design_path: str) -> None:
        self.design_path = design_path
        self.product_type = product_type
        self.products = Controller.create_products(product_type, design_path)
        self.logger = PicGeniusLogger()

    def generate_all_assets(self, output_dir: str, max_threads: int = 4):
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

        self.logger.info(
            "Start product generation: %s (to: %s)",
            product.name,
            output_dir,
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
        self.logger.info("Done %s", product.name)

    @staticmethod
    def create_products(product_type: ProductType, design_path: str) -> list[Product]:
        """Instanciate all products according to the given type and path."""

        designs_count = product_type.designs_count
        return [
            Product(product_type, product_path)
            for product_path in utils.find_product_paths(designs_count, design_path)
        ]

    def upscale_designs(self, output_dir: str):
        pass

    def generate_templates(self, output_dir: str, template_name: Optional[str] = None):
        """Generate templates."""
        for product in self.products:
            self.logger.info("Start templates generation for %s", product.name)
            ProductRenderer.generate_templates(product, output_dir)

    def generate_video(self, output_dir: str):
        pass
