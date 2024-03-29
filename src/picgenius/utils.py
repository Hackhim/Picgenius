"""Module to define utils."""
import os
from PIL import Image


# os and file related functions


def has_image_extension(path: str) -> bool:
    """Returns True if the given path ends with an image extension."""
    return path.endswith((".png", ".jpg", ".jpeg"))


def load_images(path: str) -> list[tuple[Image.Image, str]]:
    """Load all images in a folder or return single image"""
    images = []
    if os.path.isfile(path) and has_image_extension(path):
        _, design_name = extract_filename(path)
        images.append(
            (Image.open(path), design_name),
        )
    elif os.path.isdir(path):
        for file_name in os.listdir(path):
            if has_image_extension(file_name):
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


def find_product_paths(designs_count: int, design_path: str) -> list[str]:
    """Find designs paths according to the given design count."""
    if designs_count == 1:
        return find_image_file_paths(design_path)
    else:
        return find_directories_with_n_image_files(design_path, designs_count)


def find_image_file_paths(design_path: str) -> list[str]:
    """Returns a list of paths to image files."""

    is_image_file = os.path.isfile(design_path) and has_image_extension(design_path)
    if is_image_file:
        return [design_path]

    return [
        os.path.join(design_path, filename)
        for filename in os.listdir(design_path)
        if has_image_extension(filename)
    ]


def find_directories_with_n_image_files(design_path: str, image_count: int):
    """Find directories that contains n image files."""
    if not os.path.isdir(design_path):
        return []

    if is_directory_with_n_image_files(design_path, image_count):
        return [design_path]

    directories = [
        os.path.join(design_path, dir)
        for dir in os.listdir(design_path)
        if os.path.isdir(os.path.join(design_path, dir))
    ]
    return [
        directory
        for directory in directories
        if is_directory_with_n_image_files(directory, image_count)
    ]


def is_directory_with_n_image_files(path: str, count: int) -> bool:
    """Returns if the given directory has x image files."""
    return (
        os.path.isdir(path)
        and len([f for f in os.listdir(path) if has_image_extension(f)]) == count
    )
