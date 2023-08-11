from marshmallow import Schema, fields


class TestSchema(Schema):
    id = fields.Int()
    content = fields.Str()
