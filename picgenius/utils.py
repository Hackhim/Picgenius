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


def get_valid_design_paths(design_path: str, designs_count: int) -> list[str]:
    """Get valid png paths according to designs_count."""
    valid_paths = []
    if designs_count == 1:
        valid_paths.extend(get_paths_of_png_files(design_path))
    else:
        valid_paths.extend(
            _get_paths_of_dirs_containing_n_png_files(design_path, designs_count)
        )
    return valid_paths


def get_paths_of_png_files(design_path: str) -> list[str]:
    """Returns a list of paths to png files."""
    paths = []

    is_png_file = os.path.isfile(design_path) and design_path.endswith(".png")
    if is_png_file:
        paths.append(design_path)
    else:
        paths.extend(
            [
                os.path.join(design_path, filename)
                for filename in os.listdir(design_path)
                if filename.endswith(".png")
            ]
        )

    return paths


def _get_paths_of_dirs_containing_n_png_files(design_path: str, png_count: int):
    paths = []

    if not os.path.isdir(design_path):
        return paths

    if _check_path_is_directory_with_n_png_files(design_path, png_count):
        paths.append(design_path)
    else:
        directories = [
            os.path.join(design_path, dir)
            for dir in os.listdir(design_path)
            if os.path.isdir(os.path.join(design_path, dir))
        ]
        paths.extend(
            [
                directory
                for directory in directories
                if _check_path_is_directory_with_n_png_files(
                    os.path.join(directory), png_count
                )
            ]
        )

    return paths


def _check_path_is_directory_with_n_png_files(path: str, count: int) -> bool:
    return (
        os.path.isdir(path)
        and len([f for f in os.listdir(path) if f.endswith(".png")]) == count
    )
