"""Module for Controller class declaration."""
from picgenius.models import ProductType, Product
from picgenius.renderers import ProductRenderer
from picgenius import utils


class Controller:
    """Its responsibility is to call the different renderers, with according attributes."""

    @staticmethod
    def generate_all_assets(
        product_type: ProductType, design_path: str, output_dir: str
    ):
        """Create products from design_path, then generate all assets"""

        products = Controller.create_products(product_type, design_path)
        for product in products:
            ProductRenderer.generate_formatted_designs(product, output_dir)
            ProductRenderer.generate_templates(product, output_dir)
            ProductRenderer.generate_video(product, output_dir)

    @staticmethod
    def create_products(product_type: ProductType, design_path: str) -> list[Product]:
        """Instanciate all products according to the given type and path."""

        designs_count = product_type.designs_count
        return [
            Product(product_type, product_path)
            for product_path in utils.find_product_paths(designs_count, design_path)
        ]
