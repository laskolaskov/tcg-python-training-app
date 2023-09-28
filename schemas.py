from marshmallow import Schema, fields, EXCLUDE


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class TestSchema(BaseSchema):
    id = fields.Int()
    content = fields.Str()


class TokenResponse(BaseSchema):
    token = fields.Str()


class UserCredentials(BaseSchema):
    username = fields.Email(required=True)
    password = fields.Str(required=True)


class UserCredentialsWithAdmin(BaseSchema):
    username = fields.Email(required=True)
    password = fields.Str(required=True)
    is_admin = fields.Bool(load_default=False)


class OkResponse(BaseSchema):
    message = fields.Str()


class ErrorResponse(BaseSchema):
    error = fields.Str()


class CollectionCardResponse(BaseSchema):
    card_id = fields.Int()
    name = fields.Str()
    url = fields.Url()
    count = fields.Int()
    price = fields.Int()
    is_marketed = fields.Bool()


class CollectionResponse(BaseSchema):
    owner = fields.Str()
    collection = fields.List(fields.Nested(CollectionCardResponse))


class UserResponse(BaseSchema):
    cards = fields.Int()
    credits = fields.Int()
    name = fields.Email()


class UserAdminResponse(BaseSchema):
    id = fields.Int()
    name = fields.Email()
    credits = fields.Int()
    collection = fields.List(fields.Nested(CollectionCardResponse))


class UsersAdminResponse(BaseSchema):
    current = fields.Str()
    users = fields.List(fields.Nested(UserAdminResponse))


class CardAdminResponse(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    url = fields.Url()


class CardsAdminResponse(BaseSchema):
    total = fields.Str()
    cards = fields.List(fields.Nested(CardAdminResponse))


class SellUserCardRequest(BaseSchema):
    user_id = fields.Int()
    card_id = fields.Int()
    price = fields.Int()


class SellCardRequest(BaseSchema):
    card_id = fields.Int()
    price = fields.Int()


class CancelSellUserCardRequest(BaseSchema):
    user_id = fields.Int()
    card_id = fields.Int()


class CancelSellCardRequest(BaseSchema):
    card_id = fields.Int()


class BuyUserCardRequest(BaseSchema):
    buyer_id = fields.Int()
    seller_id = fields.Int()
    card_id = fields.Int()


class BuyCardRequest(BaseSchema):
    seller_id = fields.Int()
    card_id = fields.Int()
