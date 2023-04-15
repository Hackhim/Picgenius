"""Module for VideoRenderer class declaration."""

import random
import numpy as np
from moviepy.editor import ImageSequenceClip
from PIL import Image

from picgenius import processing as im
from picgenius.models import VideoSettings, Watermark
from picgenius.renderers import WatermarkRenderer


class VideoRenderer:
    """Generate video."""

    @staticmethod
    def generate_video(
        image: Image.Image, video_settings: VideoSettings
    ) -> ImageSequenceClip:
        """Generate a video according to the given video settings."""
        base_image = im.resize_and_crop(image, *video_settings.format)
        base_image = VideoRenderer._apply_watermark(
            base_image.convert("RGBA"), video_settings.watermark
        )

        frames = VideoRenderer.generate_video_frames(
            base_image, video_settings.frames, video_settings.step
        )
        # TODO: frames = VideoRenderer._generate_movement_frames(base_image, video_settings)
        np_frames = [np.array(img) for img in frames]
        video = ImageSequenceClip(np_frames, fps=20)
        return video

    @staticmethod
    def generate_video_frames(image: Image.Image, frames: int = 100, step=1):
        """Generate the frames for the video."""
        images = []
        for i in range(0, frames, step):
            tl = i
            br = image.width - i

            zoom_region = (tl, tl, br, br)
            zoom_image = image.crop(zoom_region).resize(
                image.size, resample=Image.LANCZOS
            )
            images.append(zoom_image)
        return images

    @staticmethod
    def _apply_watermark(
        image: Image.Image, watermark: Watermark | None
    ) -> Image.Image:
        watermarked_image = image
        if watermark is not None:
            watermarked_image = WatermarkRenderer.apply_watermarking(image, watermark)
        return watermarked_image

    @staticmethod
    def _generate_movement_frames(
        image: Image.Image, video_settings: VideoSettings
    ) -> list[Image.Image]:
        """Generate the frames for the video according to the video settings movement."""
        movement_functions: dict = {
            "zoom_in": VideoRenderer._generate_zoom_in_frames,
            "zoom_out": VideoRenderer._generate_zoom_out_frames,
            "slide_left": VideoRenderer._generate_slide_left_frames,
            "slide_right": VideoRenderer._generate_slide_right_frames,
        }
        movement_functions["random"] = random.choice(list(movement_functions.values()))

        assert video_settings.movement in movement_functions

        movement = movement_functions[video_settings.movement]
        return movement(image, video_settings)

    @staticmethod
    def _generate_zoom_in_frames(
        image: Image.Image, video_settings: VideoSettings
    ) -> list[Image.Image]:
        raise NotImplementedError("Not implemented yet.")  # TODO
        frames = video_settings.frames
        step = video_settings.step
        start_zoom = video_settings.start_zoom
        frame_width, frame_height = video_settings.format
        images = []

        center_x = image.width // 2
        center_y = image.height // 2

        # Calculate the maximum zoom level without going out of the image boundaries
        max_zoom = min(image.width / frame_width, image.height / frame_height)

        for i in range(0, frames, step):
            zoom = 1 + i * (max_zoom + 1) / (frames + 1)
            new_width = int(image.width / zoom)
            new_height = int(image.height / zoom)

            tl_x = center_x - new_width // 2
            tl_y = center_y - new_height // 2
            br_x = center_x + new_width // 2
            br_y = center_y + new_height // 2

            zoom_region = (tl_x, tl_y, br_x, br_y)
            zoom_image = image.crop(zoom_region).resize(
                (frame_width, frame_height), resample=Image.LANCZOS
            )
            images.append(zoom_image)

        return images

    @staticmethod
    def _generate_zoom_out_frames(
        image: Image.Image, video_settings: VideoSettings
    ) -> list[Image.Image]:
        raise NotImplementedError("Not implemented yet.")  # TODO
        frames = video_settings.frames
        step = video_settings.step
        images = []

        for i in range(frames, 0, -step):
            tl = i
            br = image.width - i
            zoom_region = (tl, tl, br, br)
            zoom_image = image.crop(zoom_region).resize(
                image.size, resample=Image.LANCZOS
            )
            images.append(zoom_image)

        return images

    @staticmethod
    def _generate_slide_left_frames(
        image: Image.Image, video_settings: VideoSettings
    ) -> list[Image.Image]:
        raise NotImplementedError("Not implemented yet.")  # TODO
        frames = video_settings.frames
        step = video_settings.step
        start_zoom = video_settings.start_zoom
        images = []

        # Calculate the initial zoomed image
        zoomed_width = int(image.width * start_zoom / 100)
        zoomed_height = int(image.height * start_zoom / 100)
        zoomed_image = image.resize(
            (zoomed_width, zoomed_height), resample=Image.LANCZOS
        )

        # Calculate the initial position offset
        initial_offset = frames // 2

        for i in range(0, frames, step):
            left = i - initial_offset
            right = left + image.width
            slide_region = (left, 0, right, image.height)

            slide_frame = zoomed_image.crop(slide_region).resize(
                image.size, resample=Image.LANCZOS
            )
            images.append(slide_frame)

        return images

    @staticmethod
    def _generate_slide_right_frames(
        image: Image.Image, video_settings: VideoSettings
    ) -> list[Image.Image]:
        raise NotImplementedError("Not implemented yet.")  # TODO
        frames = video_settings.frames
        step = video_settings.step
        images = []

        for i in range(0, frames, step):
            left = -i + image.width // 2
            right = left + image.width
            slide_region = (left, 0, right, image.height)
            slide_image = image.crop(slide_region).resize(
                image.size, resample=Image.LANCZOS
            )
            images.append(slide_image)

        return images
