"""Module for TestTemplateRenderer class declaration."""
from pathlib import Path
from PIL import Image
from picgenius.models import Template, TemplateElement, Design
from picgenius.renderers import TemplateRenderer


class TestTemplateRenderer:
    """Test TemplateRenderer"""

    design1: Design
    design2: Design
    template: Template
    output_path: str

    def setup_method(self):
        """Setup test data."""
        self.design1 = Design(path="./tests/workdir/designs/paint-explosion.png")
        self.design2 = Design(path="./tests/workdir/designs/paint-smoke.png")
        self.template = Template(
            path="./tests/workdir/templates/3-table.png",
            elements=[
                TemplateElement(position=(428, 186), size=(480, 685)),
                TemplateElement(position=(998, 186), size=(480, 685)),
            ],
            watermark=None,
        )
        self.output_path = "./tests/workdir/output/test-template-render.png"

    def test_generate_template(self):
        """Test generate_templates"""
        designs = [self.design1, self.design2]
        result = TemplateRenderer.generate_template(self.template, designs)

        assert isinstance(result, Image.Image)
        result.save(self.output_path)
        assert Path(self.output_path).is_file()

    def teardown_method(self):
        """Clean data."""
        output_file = Path(self.output_path)
        if output_file.is_file():
            output_file.unlink()
