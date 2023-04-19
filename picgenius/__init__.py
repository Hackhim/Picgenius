"""Shortcuts the imports."""
# from jsonschema import validate
#
# CONFIG_SCHEMA = {
#    "type": "object",
#    "additionalProperties": False,
#    "properties": {
#        "formats": {
#            "type": "array",
#            "items": {
#                "type": "object",
#                "additionalProperties": False,
#                "required": ["ppi", "inches"],
#                "properties": {
#                    "ppi": {
#                        "type": "number",
#                    },
#                    "inches": {
#                        "type": "array",
#                        "items": {"type": "number"},
#                        "minItems": 2,
#                        "maxItems": 2,
#                    },
#                },
#            },
#        },
#        "mockups": {
#            "type": "object",
#            "additionalProperties": {
#                "type": "object",
#                "required": ["designs-count", "templates"],
#                "properties": {
#                    "designs-count": {"type": "number"},
#                    "templates": {
#                        "type": "array",
#                        "items": {
#                            "type": "object",
#                            "required": ["template_path", "elements"],
#                            "properties": {
#                                "template_path": {"type": "string"},
#                                "elements": {
#                                    "type": "array",
#                                    "items": {
#                                        "type": "object",
#                                        "required": ["position", "size"],
#                                        "properties": {
#                                            "position": {
#                                                "type": "array",
#                                                "items": {"type": "number"},
#                                                "minItems": 2,
#                                                "maxItems": 2,
#                                            },
#                                            "size": {
#                                                "type": "array",
#                                                "items": {"type": "number"},
#                                                "minItems": 2,
#                                                "maxItems": 2,
#                                            },
#                                        },
#                                    },
#                                },
#                                "watermark": {"type": "string"},
#                            },
#                        },
#                    },
#                    "watermarks": {
#                        "type": "object",
#                        "additionalProperties": {
#                            "type": "object",
#                            "additionalProperties": False,
#                            "required": [
#                                "font_path",
#                                "text",
#                            ],
#                            "properties": {
#                                "font_path": {"type": "string"},
#                                "text": {"type": "string"},
#                                "color": {
#                                    "type": "array",
#                                    "items": {"type": "number"},
#                                    "minItems": 4,
#                                    "maxItems": 4,
#                                },
#                                "position": {
#                                    "type": "array",
#                                    "items": {"type": ["string", "number"]},
#                                    "minItems": 2,
#                                    "maxItems": 2,
#                                },
#                                "margin": {"type": "number"},
#                                "width": {"type": ["string", "number"]},
#                                "textbox": {
#                                    "type": "object",
#                                    "required": ["padding", "color"],
#                                    "properties": {
#                                        "padding": {
#                                            "type": "array",
#                                            "items": {"type": "number"},
#                                            "minItems": 4,
#                                            "maxItems": 4,
#                                        },
#                                        "color": {
#                                            "type": "array",
#                                            "items": {"type": "number"},
#                                            "minItems": 4,
#                                            "maxItems": 4,
#                                        },
#                                    },
#                                },
#                            },
#                        },
#                    },
#                    "video": {
#                        "type": "object",
#                        "properties": {
#                            "movement": {"type": "string"},
#                            "start_zoom": {"type": "string"},
#                            "step": {"type": "number"},
#                            "frames": {"type": "number"},
#                            "fps": {"type": "number"},
#                            "watermark": {"type": "string"},
#                        },
#                    },
#                },
#            },
#        },
#    },
#    "required": ["formats", "mockups"],
# }
