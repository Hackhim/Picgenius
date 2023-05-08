"""Module to test ProductRenderer."""
import os

from picgenius.models import (
    Product,
    ProductType,
    Template,
    TemplateElement,
    Format,
    VideoSettings,
    Watermark,
    Textbox,
)
from picgenius.renderers import ProductRenderer


class TestProductRenderer:
    """Test ProductRenderer."""

    BASE_WORKDIR = "./tests/workdir"
    OUTPUT_DIR = os.path.join(BASE_WORKDIR, "output")

    product: Product

    def setup_method(self):
        """Setup data."""
        self.product = Product(
            design_path=self._build_path("designs/set-4-designs"),
            type=ProductType(
                designs_count=4,
                formats=[
                    Format(ppi=300, inches=(8, 10)),
                    Format(ppi=300, inches=(10, 14)),
                ],
                templates=[
                    Template(
                        path=self._build_path("templates/3-table.png"),
                        elements=[
                            TemplateElement(position=(428, 186), size=(480, 685)),
                            TemplateElement(position=(998, 186), size=(480, 685)),
                        ],
                        watermark=Watermark(
                            text="PicGenius",
                            font_path="./workdir/CS_Gordon/CS Gordon Vintage.otf",
                            color=(0, 0, 0, 255),
                            textbox=Textbox(
                                (50, 75, 50, 50), color=(255, 255, 255, 127)
                            ),
                        ),
                    ),
                    Template(
                        path=self._build_path("templates/1-base.png"),
                        elements=[
                            TemplateElement(position=(443, 176), size=(490, 732)),
                            TemplateElement(position=(1076, 176), size=(490, 732)),
                            TemplateElement(position=(443, 1055), size=(490, 732)),
                            TemplateElement(position=(1076, 1055), size=(490, 732)),
                        ],
                    ),
                ],
                video_settings=VideoSettings(
                    movement="zoom_in",
                    watermark=Watermark(
                        text="PicGenius",
                        font_path="./workdir/CS_Gordon/CS Gordon Vintage.otf",
                        color=(0, 0, 0, 255),
                        textbox=Textbox((50, 75, 50, 50), color=(255, 255, 255, 127)),
                    ),
                ),
            ),
        )

    def _build_path(self, *args) -> str:
        return os.path.join(self.BASE_WORKDIR, *args)

    def test_generate_product_templates(self):
        """Test templates generation."""
        product = self.product
        ProductRenderer.generate_templates(product, self.OUTPUT_DIR)

        assert os.path.exists(
            os.path.join(
                self.OUTPUT_DIR,
                product.name,
                ProductRenderer.VISUALS_FOLDER,
                "3-table.png",
            )
        )
        assert os.path.exists(
            os.path.join(
                self.OUTPUT_DIR,
                product.name,
                ProductRenderer.VISUALS_FOLDER,
                "1-base.png",
            )
        )

    def test_generate_product_video(self):
        """Test video generation."""
        product = self.product
        ProductRenderer.generate_video(product, self.OUTPUT_DIR)

        # Assert that the output video file was created
        assert os.path.exists(
            os.path.join(
                self.OUTPUT_DIR,
                product.name,
                ProductRenderer.VISUALS_FOLDER,
                ProductRenderer.VIDEO_FILENAME,
            )
        )

    def test_generate_formatted_designs(self):
        """Test formatted designs generation."""
        product = self.product

        ProductRenderer.generate_formatted_designs(product, self.OUTPUT_DIR)

        # Assert that the output files were created
        # assert os.path.exists(
        #    os.path.join(
        #        self.OUTPUT_DIR, product.name, ProductRenderer.FORMATTED_DESIGNS_FOLDER
        #    )
        # )
