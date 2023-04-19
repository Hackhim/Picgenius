"""Module for TestTemplateRenderer class declaration."""
from pathlib import Path
from PIL import Image
from picgenius.models import Template, TemplateElement, Design
from picgenius.renderers import TemplateRenderer


class TestTemplateRenderer:
    """Test TemplateRenderer"""

    design1: Design
    design2: Design
    design3: Design
    design4: Design
    template: Template
    template_slant: Template
    output_path: str
    output_path_slant: str

    def setup_method(self):
        """Setup test data."""
        self.design1 = Design(path="./tests/workdir/designs/paint-explosion.png")
        self.design2 = Design(path="./tests/workdir/designs/paint-smoke.png")
        self.design3 = Design(path="./tests/workdir/designs/flowers-1.png")
        self.design4 = Design(path="./tests/workdir/designs/flowers-2.png")
        self.template = Template(
            path="./tests/workdir/templates/3-table.png",
            elements=[
                TemplateElement(position=(428, 186), size=(480, 685)),
                TemplateElement(position=(998, 186), size=(480, 685)),
            ],
            watermark=None,
        )

        self.template_slant = Template(
            path="./tests/workdir/templates/template-biais-1.png",
            elements=[
                TemplateElement(
                    position=(
                        (110, 172),
                        (286, 198),
                        (110, 533),
                        (286, 530),
                    ),
                ),
                TemplateElement(
                    position=(
                        (340, 207),
                        (469, 226),
                        (340, 528),
                        (469, 528),
                    ),
                ),
            ],
        )
        self.output_path = "./tests/workdir/output/test-template-render.png"
        self.output_path_slant = "./tests/workdir/output/test-template-render-slant.png"

    def test_generate_template(self):
        """Test generate_templates"""
        designs = [self.design1, self.design2]
        result = TemplateRenderer.generate_template(self.template, designs)

        assert isinstance(result, Image.Image)
        result.save(self.output_path)
        assert Path(self.output_path).is_file()

    def test_generate_slanted_template(self):
        """Test template generation for slanted canvas."""
        designs = [self.design3, self.design4]
        result = TemplateRenderer.generate_template(self.template_slant, designs)

        assert isinstance(result, Image.Image)
        result.save(self.output_path_slant)
        assert Path(self.output_path_slant).is_file()
