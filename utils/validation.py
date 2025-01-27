# utils/validation.py
from marshmallow import Schema, fields, validates

class ImageRequestSchema(Schema):
    session_id = fields.Str(required=True)
    template_type = fields.Str(required=True)
    text = fields.Str(required=False)
    sub_text = fields.Str(required=False)
    arrow = fields.Str(required=False)

    @validates('template_type')
    def validate_template(self, value):
        if value not in TEMPLATE_CONFIG:
            raise ValueError(f"Invalid template type: {value}")