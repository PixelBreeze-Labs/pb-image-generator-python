# templates/__init__.py
from PIL import Image, ImageDraw, ImageFont
import os

TEMPLATE_CONFIG = {
    'quotes_writings_art': {
        'size': (1080, 1080),
        'font': 'static/fonts/BASKVILL.TTF',
        'colors': {
            'background': '#ffffff',
            'text': '#000000'
        }
    },
    # Add other template configs
}

class TemplateManager:
    def __init__(self):
        self._load_resources()

    def _load_resources(self):
        """Pre-load common resources like fonts"""
        self.fonts = {}
        for template in TEMPLATE_CONFIG.values():
            font_path = template.get('font')
            if font_path and font_path not in self.fonts:
                self.fonts[font_path] = ImageFont.truetype(font_path)

    def get_template(self, template_type):
        """Get template configuration"""
        return TEMPLATE_CONFIG.get(template_type)

template_manager = TemplateManager()