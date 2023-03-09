"""Module for MockupGenerator class definition."""
import os
from PIL import Image, ImageDraw, ImageFont


class MockupGenerator:
    """Class that handle Mockup Generating."""

    def generate_mockups(
        self, design_path: str, mockups_path: str, template_conf: dict
    ):
        if not os.path.isdir(mockups_path):
            raise AttributeError("mockup_path must be a folder.")

        multiple_designs: bool = int(template_conf["designs_count"]) > 1

        if multiple_designs:
            raise NotImplementedError("TODO: MultipleDesigns mockups.")
        else:
            self.generate_1_design_mockups(design_path, mockups_path, template_conf)

    def generate_1_design_mockups(
        self, design_path: str, mockups_path: str, template_conf: dict
    ):
        design = Image.open(design_path)
        design_filename, design_name = self.extract_filename(design_path)
        new_mockup_path = os.path.join(mockups_path, design_name)
        os.makedirs(new_mockup_path, exist_ok=True)

        print(f" [*] Generating design: {design_name}")

        # print("\t[*] Generating gif..")
        # TODO: generate_video(design_path, f"{design_mockups_dir_path}/design_video.mp4")

        for template in template_conf["templates"]:
            mockup_filename, _ = self.extract_filename(template_conf["template_path"])

            print(f"\t[*] Generating mockup: {mockup_filename}")

            mockup_path = os.path.join(new_mockup_path, mockup_filename)
            mockup = generate_mockup(template_conf, design_path)
            mockup = add_text_to_image(mockup, "SIMAAKER SHOP")
            mockup.save(mockup_path)

    @staticmethod
    def _load_images(path: str):
        """Load all PNG images in a folder or return single image"""
        if os.path.isfile(path) and path.endswith(".png"):
            return Image.open(path)
        elif os.path.isdir(path):
            images = []
            for file_name in os.listdir(path):
                if file_name.endswith(".png"):
                    file_path = os.path.join(path, file_name)
                    images.append(Image.open(file_path))
            return images
        else:
            raise ValueError("Invalid path specified")

    @staticmethod
    def extract_filename(path: str) -> tuple[str, str]:
        """
        Extracts the filename and filename without extension
        from a given path and returns them as a tuple
        """
        filename = os.path.basename(path)
        filename_without_extension = os.path.splitext(filename)[0]
        return (filename, filename_without_extension)

    @staticmethod
    def ensure_path_exists(path):
        """Ensures that the given path exists by creating any missing directories."""
        os.makedirs(path, exist_ok=True)
