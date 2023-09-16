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


class OkResponse(Schema):
    message = fields.Str()


class ErrorResponse(Schema):
    error = fields.Str()


class CollectionCardResponse(Schema):
    card_id = fields.Int()
    name = fields.Str()
    url = fields.Url()
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

class UserAdminResponse(Schema):
    id = fields.Int()
    name = fields.Email()
    credits = fields.Int()
    collection = fields.List(fields.Nested(CollectionCardResponse))

class UsersAdminResponse(Schema):
    current = fields.Str()
    users = fields.List(fields.Nested(UserAdminResponse))

class CardAdminResponse(Schema):
    id = fields.Int()
    name = fields.Str()
    url = fields.Url()

class CardsAdminResponse(Schema):
    total = fields.Str()
    cards = fields.List(fields.Nested(CardAdminResponse))

class SellUserCardRequest(Schema):
    user_id = fields.Int()
    card_id = fields.Int()
    price = fields.Int()

class SellCardRequest(Schema):
    card_id = fields.Int()
    price = fields.Int()

class CancelSellUserCardRequest(Schema):
    user_id = fields.Int()
    card_id = fields.Int()

class CancelSellCardRequest(Schema):
    card_id = fields.Int()

class BuyUserCardRequest(Schema):
    buyer_id = fields.Int()
    seller_id = fields.Int()
    card_id = fields.Int()

class BuyCardRequest(Schema):
    seller_id = fields.Int()
    card_id = fields.Int()
