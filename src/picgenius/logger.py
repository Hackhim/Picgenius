"""Module for PicGeniusLogger class declaration."""
import logging
import os
import sys
from typing import Optional


class PicGeniusLogger(logging.Logger):
    """PicGenius Logger"""

    def __init__(
        self,
        name: str = "picgenius",
        log_level: Optional[int] = None,
        log_file: Optional[str] = None,
    ):
        if log_level is not None:
            super().__init__(name, log_level)
        else:
            super().__init__(name)

        # Configure log formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

        # Configure the console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        # Configure the file handler if a log_file is provided
        if log_file:
            if not os.path.exists(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)


# Add the custom logger to the logging system
logging.setLoggerClass(PicGeniusLogger)
