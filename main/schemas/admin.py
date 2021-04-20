from marshmallow import fields
from .base import BaseSchema


class PageSchema(BaseSchema):
    page = fields.Integer(validate=lambda n: n >= 1, required=True)
