"""
Package for Picgenius Renderers.
Renderers have the concern to run the logic to generate the products, templates and so on.
"""
from .watermark import WatermarkRenderer
from .template import TemplateRenderer
from .video import VideoRenderer
from .product import ProductRenderer
from .design import DesignRenderer
