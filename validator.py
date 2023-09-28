from database import Database
from marshmallow import ValidationError
from schemas import UserCredentialsWithAdmin, UserCredentials, SellCardRequest
from models import UserModel, CardModel, CollectionModel


def validate_signup(input: dict, db: Database):
    signupSchema = UserCredentialsWithAdmin()
    result = signupSchema.load(input)

    # checking for existing user
    user = db.getUserByName(result["username"])
    if user:
        raise ValidationError(
            {
                "username": [
                    "This username already exists! Get your token at /auth and start exploring!"
                ]
            }
        )

    return result


def validate_auth(input: dict, db: Database) -> UserModel:
    authSchema = UserCredentials()
    authSchema.load(input)

    # load user
    user = db.getUserByName(input.get("username"))

    if not user:
        raise ValidationError("Could not verify user credentials")

    return user


def validate_sell_card(input: dict, db: Database, current_user: UserModel) -> CollectionModel:
    (SellCardRequest()).load(input)

    # load card
    card = db.session.get(CardModel, input.get("card_id"))
    if not card:
        raise ValidationError(f"No card with id: {input.get('card_id')}")

    collection = db.getCollection(current_user, card)
    if not collection or collection.count <= 0:
        raise ValidationError(f"You does not own {card.name}")

    return collection
