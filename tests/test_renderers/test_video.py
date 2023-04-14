"""Module for TestTemplateRenderer class declaration."""
import os
from pathlib import Path
from PIL import Image
from picgenius.models import VideoSettings, Watermark, Design
from picgenius.renderers import VideoRenderer


class TestVideoRenderer:
    """Test TemplateRenderer"""

    design: Design
    video_settings: VideoSettings
    output_dir: str

    def setup_method(self):
        """Setup test data."""
        self.design = Design(path="./tests/workdir/designs/paint-explosion.png")

        self.video_settings = VideoSettings(
            "random",
            watermark=Watermark(
                "./workdir/CS_Gordon/CS Gordon Vintage.otf",
                "PicGenius",
                color=(127, 127, 127, 127),
            ),
        )
        self.output_dir = "./tests/workdir/output/"

    def test_generate_video(self):
        """Test generate_video"""
        output_path = os.path.join(self.output_dir, "random.mp4")
        image = Image.open(self.design.path)
        video = VideoRenderer.generate_video(image, self.video_settings)
        video.write_videofile(output_path, verbose=False, logger=None)
        image.close()

    def test_zoom_in(self):
        """Test zoom in generation."""
        self._run_video_generation("zoom_in")

    def test_zoom_out(self):
        """Test zoom out generation."""
        self._run_video_generation("zoom_out")

    def test_slide_left(self):
        """Test slide left generation."""
        self._run_video_generation("slide_left")

    def test_slide_right(self):
        """Test slide right generation."""
        self._run_video_generation("slide_right")

    def _run_video_generation(self, movement: str):
        output_path = os.path.join(self.output_dir, f"{movement}.mp4")
        self.video_settings.movement = movement
        image = Image.open(self.design.path)
        video = VideoRenderer.generate_video(image, self.video_settings)
        video.write_videofile(output_path, verbose=False, logger=None)
        image.close()

    # def teardown_method(self):
    #    """Clean data."""
    #    output_file = Path(self.output_path)
    #    if output_file.is_file():
    #        output_file.unlink()
