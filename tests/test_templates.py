# tests/test_templates.py
import unittest
from PIL import Image
from templates import template_manager

class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.template_manager = template_manager

    def test_template_loading(self):
        template = self.template_manager.get_template('quotes_writings_art')
        self.assertIsNotNone(template)
        self.assertIn('size', template)

    def test_image_generation(self):
        params = {
            'text': 'Test text',
            'sub_text': 'Subtext'
        }
        image = generate_template_image('quotes_writings_art', params)
        self.assertIsInstance(image, Image.Image)