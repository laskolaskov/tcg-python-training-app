from marshmallow import Schema, fields


class TestSchema(Schema):
    id = fields.Int()
    content = fields.Str()


class TokenResponse(Schema):
    token = fields.Str()


class UserCredentials(Schema):
    username = fields.Email()
    password = fields.Str()


class SignupRequest(Schema):
    username = fields.Email()
    password = fields.Str()


class UserCreatedResponse(Schema):
    message = fields.Str()


class ErrorResponse(Schema):
    error = fields.Str()


class CollectionCardResponse(Schema):
    name = fields.Str()
    url = fields.Str()
    count = fields.Int()
    price = fields.Int()
    is_marketed = fields.Bool()


class CollectionResponse(Schema):
    owner = fields.Str()
    collection = fields.List(fields.Nested(CollectionCardResponse))


class UserResponse(Schema):
    cards = fields.Int()
    credits = fields.Int()
    name = fields.Email()
