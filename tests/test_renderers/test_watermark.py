"""Module to test Watermark Generation"""
from PIL import Image

from picgenius.models import Watermark, Textbox
from picgenius.renderers import WatermarkRenderer


class TestWatermarkRenderer:
    """Test class for WatermarkRenderer"""

    sample_image: Image.Image
    watermark: Watermark

    def setup_method(self):
        """Setup test data."""
        self.sample_image = Image.new("RGBA", (1000, 1000), (255, 255, 255))
        self.watermark = Watermark(
            font_path="./workdir/CS_Gordon/CS Gordon Vintage.otf",
            text="TEST WATERMARK",
            color=(0, 0, 0, 255),
            position=("center", "bottom"),
            margin=50,
            width="50%",
            textbox=Textbox(color=(255, 255, 255, 128), padding=(10, 10, 10, 10)),
        )

    def test_apply_watermarking(self):
        """test_apply_watermarking"""
        watermarked = WatermarkRenderer.apply_watermarking(
            self.sample_image, self.watermark
        )
        assert isinstance(watermarked, Image.Image)
