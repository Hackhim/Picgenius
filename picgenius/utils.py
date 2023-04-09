"""Module to define utils."""
import os
from PIL import Image


# os and file related functions


def load_images(path: str) -> list[tuple[Image.Image, str]]:
    """Load all PNG images in a folder or return single image"""
    images = []
    if os.path.isfile(path) and path.endswith(".png"):
        _, design_name = extract_filename(path)
        images.append(
            (Image.open(path), design_name),
        )
    elif os.path.isdir(path):
        for file_name in os.listdir(path):
            if file_name.endswith(".png"):
                file_path = os.path.join(path, file_name)
                _, design_name = extract_filename(file_path)
                images.append(
                    (Image.open(file_path), design_name),
                )
    else:
        raise ValueError("Invalid path specified")
    return images


def extract_filename(path: str) -> tuple[str, str]:
    """
    Extracts the filename and filename without extension
    from a given path and returns them as a tuple
    """
    filename = os.path.basename(path)
    filename_without_extension = os.path.splitext(filename)[0]
    return (filename, filename_without_extension)
