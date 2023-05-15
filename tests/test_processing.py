"""Module to test image processing functions."""
import os
from PIL import Image

from picgenius import processing as im


class TestProcessing:
    """Test class for image processing"""

    image: Image.Image
    image_path: str = "tests/workdir/designs/flowers-1.png"
    output_path: str = "tests/workdir/output/cropped-flowers-1.png"

    def setup_method(self):
        """Setup test data."""
        self.image = Image.open(self.image_path)

    def test_crop_to_ratio(self):
        """Test crop_to_ratio(...) function."""
        cropped_image = im.crop_to_ratio(self.image, (1, 1))
        assert isinstance(cropped_image, Image.Image)
        cropped_image.save(self.output_path)
        os.path.exists(self.output_path)
