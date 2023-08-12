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
    admin = fields.Bool()

class UserCreatedResponse(Schema):
    message = fields.Str()

class ErrorResponse(Schema):
    error = fields.Str()
