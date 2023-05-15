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

    plant1: Design
    plant2: Design
    plant3: Design

    template: Template
    template_2: Template
    template_3: Template
    not_path_template: Template

    output_path: str
    output_path_2: str
    output_path_3: str

    def setup_method(self):
        """Setup test data."""
        self.design1 = Design(path="./tests/workdir/designs/paint-explosion.png")
        self.design2 = Design(path="./tests/workdir/designs/paint-smoke.png")
        self.design3 = Design(path="./tests/workdir/designs/flowers-1.png")
        self.design4 = Design(path="./tests/workdir/designs/flowers-2.png")

        self.plant1 = Design(path="./tests/workdir/designs/plants/plant-1.png")
        self.plant2 = Design(path="./tests/workdir/designs/plants/plant-2.png")
        self.plant3 = Design(path="./tests/workdir/designs/plants/plant-3.png")

        self.template = Template(
            path="./tests/workdir/templates/3-table.png",
            elements=[
                TemplateElement(position=(428, 186), size=(480, 685)),
                TemplateElement(position=(998, 186), size=(480, 685)),
            ],
            watermark=None,
        )

        self.template_2 = Template(
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

        self.template_3 = Template(
            path="./tests/workdir/templates/template-biais-3.png",
            elements=[
                TemplateElement(
                    position=(
                        (502, 358),
                        (1158, 416),
                        (502, 1455),
                        (1158, 1457),
                    ),
                ),
                TemplateElement(
                    position=(
                        (1259, 426),
                        (1840, 480),
                        (1259, 1459),
                        (1840, 1461),
                    ),
                    ratio=(1, 1),
                ),
                TemplateElement(
                    position=(
                        (1931, 489),
                        (2449, 536),
                        (1931, 1463),
                        (2449, 1465),
                    ),
                    ratio=(3, 4),
                ),
            ],
        )

        self.not_path_template = Template(
            filename="no_path_template.jpg",
            elements=[
                TemplateElement(position=(428, 186), size=(480, 685)),
                TemplateElement(position=(998, 186), size=(480, 685)),
            ],
            background_color=(255, 255, 255),
        )

        self.output_path = "./tests/workdir/output/test-template-render-1.png"
        self.output_path_2 = "./tests/workdir/output/test-template-render-2.png"
        self.output_path_3 = "./tests/workdir/output/test-template-render-3.png"

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
        result = TemplateRenderer.generate_template(self.template_2, designs)

        assert isinstance(result, Image.Image)
        result.save(self.output_path_2)
        assert Path(self.output_path_2).is_file()

    def test_generate_template_3(self):
        """Test template generation for slanted canvas."""
        designs = [self.plant1, self.plant2, self.plant3]
        result = TemplateRenderer.generate_template(self.template_3, designs)

        assert isinstance(result, Image.Image)
        result.save(self.output_path_3)
        assert Path(self.output_path_3).is_file()

    def test_generate_no_path_template(self):
        """Test template generation for slanted canvas."""

        designs = [
            Design(path="./tests/workdir/designs/flowers-1.png"),
            # Design(path="./tests/workdir/designs/flowers-2.png"),
        ]
        not_path_template = Template(
            filename="no_path_template.jpg",
            elements=[
                TemplateElement(position=(0, 0), size=(2000, 2000), zoom=3),
                TemplateElement(position=(998, 186), size=(480, 685)),
            ],
            background_color=(240, 240, 240),
        )
        output_path = f"tests/workdir/output/{not_path_template.filename}"

        result = TemplateRenderer.generate_template(not_path_template, designs)
        result = result.convert("RGB")

        assert isinstance(result, Image.Image)
        result.save(output_path)
        assert Path(output_path).is_file()
