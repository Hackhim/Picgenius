"""Module for Video class declaration."""


class Video:
    """Video has the responsibility to generate a short video for the given design."""

    def __init__(
        self,
        movement: str,
        start_zoom: str,
        step: int,
        frames: int,
        fps: int,
    ) -> None:
        self.movement = movement
        self.start_zoom = start_zoom
        self.step = step
        self.frames = frames
        self.fps = fps
