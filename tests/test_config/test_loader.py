"""Module for TestConfigLoader class declaration."""
from picgenius.models import VideoSettings, Watermark, Design
from picgenius.config import ConfigLoader


class TestConfigLoader:
    """Test ConfigLoader"""

    config_path: str

    def setup_method(self):
        """Setup test data."""
        self.config_path = "./tests/picgenius.yml"

    def test_load_config(self):
        """Test generate_video"""

        config_loader = ConfigLoader(self.config_path)
        config_loader.load()

        assert "formats" in config_loader.global_config
        assert "watermarks" in config_loader.global_config
        assert len(config_loader.product_types.items()) == 2
