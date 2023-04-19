"""Module for Controller class declaration."""
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

    def generate_all_assets(self, output_dir: str):
        """Create products from design_path, then generate all assets"""

        for product in self.products:
            self.format_product_designs(product, output_dir)
            self.generate_product_templates(product, output_dir)
            self.generate_product_video(product, output_dir)

    def format_product_designs(self, product: Product, output_dir: str):
        """Generate formatted designs for the given product."""
        self.logger.info(
            "Start %s formatted design generation to: %s", product.name, output_dir
        )
        ProductRenderer.generate_formatted_designs(product, output_dir)

    def generate_product_templates(self, product: Product, output_dir: str):
        """Generate product templates."""

        self.logger.info(
            "Start %s templates generation to: %s", product.name, output_dir
        )
        ProductRenderer.generate_templates(product, output_dir)

    def generate_product_video(self, product: Product, output_dir: str):
        """Generate product video."""
        self.logger.info("Start %s video generation to: %s", product.name, output_dir)
        ProductRenderer.generate_video(product, output_dir)

    @staticmethod
    def create_products(product_type: ProductType, design_path: str) -> list[Product]:
        """Instanciate all products according to the given type and path."""

        designs_count = product_type.designs_count
        return [
            Product(product_type, product_path)
            for product_path in utils.find_product_paths(designs_count, design_path)
        ]
