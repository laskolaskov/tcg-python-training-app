import os
from flask import Flask
from flask import redirect, request, jsonify
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_plugins.webframeworks.flask import FlaskPlugin
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from database import Database

# need to import anything from the schemas, without this it does NOT work ???
from schemas import (
    TestSchema,
)
import jwt
from datetime import datetime, timedelta
from functools import wraps
from models import UserModel, CardModel, CollectionModel

# load .env variables
load_dotenv()
db_url = os.getenv("DATABASE_URL")
secret_key = (
    os.getenv("SECRET_KEY")
    or "lelemaleneemnogosecrettoqkey!!!!133769420itn_razni_sme6ni_cifi4ki"
)

# create database object
db = Database(db_url)
db.init_db()  # rebuilds DB schema, be careful!!!


# Create an APISpec
spec = APISpec(
    title="TCG Game!",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
spec.components.security_scheme(
    component_id="token",
    component={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
)


app = Flask(__name__)


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        # return 401 if token is not passed
        if not token:
            return jsonify({"error": "Token is missing !!"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(jwt=token, key=secret_key, algorithms="HS256")
            current_user: UserModel = db.getUserByName(data["public_id"])
        except:
            return jsonify({"error": "Token is invalid !!"}), 401
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# decorator to check admin access
def admin_required(f):
    @wraps(f)
    def decorated(current_user: UserModel, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"error": "You are not admin!"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


@app.errorhandler(404)
def page_not_found(e):
    return (f"{e}", 404)


@app.route("/")
# redirect to Swagger UI page
def index():
    return redirect("/api")


@app.route("/test")
def test():
    return "test"


@app.route("/auth", methods=["POST"])
def auth():
    """Authenticate.
    ---
    post:
      tags:
        - Authenticate
      summary: Get access token.
      description: Get access token.
      requestBody:
        content:
          application/json:
            schema: UserCredentials
          application/x-www-form-urlencoded:
            schema: UserCredentials
      responses:
        200:
          description: OK  
          content:
            application/json:
              schema: TokenResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    if request.content_type == "application/json":
        auth = request.json
    else:
        auth = request.form

    if not auth or not auth.get("username") or not auth.get("password"):
        # returns 400 if any email or / and password is missing
        return ({"error": "Please provide user credentials"}, 400)

    # load user
    user: UserModel = db.getUserByName(auth.get("username"))

    if not user:
        return ({"error": "Could not verify user credentials"}, 403)

    if check_password_hash(user.password, auth.get("password")):
        # generates the JWT Token
        token = jwt.encode(
            {
                "public_id": user.username,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            secret_key,
        )
        return ({"token": token}, 200)

    # returns 403 if password is wrong
    return ({"error": "Could not verify user credentials"}, 403)


@app.route("/signup", methods=["POST"])
def signup():
    """Signup.
    ---
    post:
      tags:
        - Authenticate
      summary: Create new user.
      description: Create new user.
      requestBody:
        content:
          application/json:
            schema: SignupRequest
          application/x-www-form-urlencoded:
            schema: SignupRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        data = request.json
    else:
        data = request.form

    if not data or not data.get("username") or not data.get("password"):
        # returns 400 if any email or / and password is missing
        return ({"error": "Please provide username and password"}, 400)

    # gets email and password
    username = data.get("username")
    password = data.get("password")
    is_admin = data.get("admin") or False

    # checking for existing user
    user = db.getUserByName(username)
    if user:
        return (
            {
                "message": "This username already exists! Get your token at /auth and start exploring!"
            },
            400,
        )

    db.insertUser(username, generate_password_hash(password), is_admin)

    return (
        {
            "message": "Successfully registered. Get your token at /auth and go check your starting collection at '/my/collection'!"
        },
        200,
    )


@app.route("/my/collection", methods=["GET"])
@token_required
def my_collection(current_user: UserModel):
    """My cards collection.
    ---
    get:
      tags:
        - My Data
      summary: My cards collection.
      description: My cards collection.
      security:
        - token: []
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: CollectionResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    return {
        "owner": current_user.username,
        "collection": [
            {
                "card_id": collection.card_id,
                "name": collection.card.name,
                "url": collection.card.url,
                "count": collection.count,
                "price": collection.price,
                "is_marketed": collection.is_marketed,
            }
            for collection in current_user.collections
        ],
    }


@app.route("/my/user", methods=["GET"])
@token_required
def my_user(current_user: UserModel):
    """My user information.
    ---
    get:
      tags:
        - My Data
      summary: My user information.
      description: My user information.
      security:
        - token: []
      responses:
        200:
          description: Ok
          content:
            application/json:
              schema: UserResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    return {
        "name": current_user.username,
        "credits": current_user.credits,
        "cards": len(current_user.collections),
    }


@app.route("/market", methods=["GET"])
@token_required
def market(current_user: UserModel):
    """Marketplace.
    ---
    get:
      tags:
        - Market
      summary: Marketplace.
      security:
        - token: []
      responses:
        200:
          description: Ok
          content:
            application/json:
              schema: OkResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    marketed = db.getMarketedCollections()

    return {
        "you": current_user.username,
        "market": [
            {
                "card_id": c.card_id,
                "card_name": c.card.name,
                "seller_id": c.user_id,
                "seller_name": c.user.username,
                "price": c.price,
            }
            for c in marketed
        ],
    }


@app.route("/sell", methods=["POST"])
@token_required
def sell_card(current_user: UserModel):
    """Put one of your cards on the market.
    ---
    post:
      tags:
        - Market
      summary: Put one of your cards on the market.
      description: Put one of your cards on the market.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: SellCardRequest
          application/x-www-form-urlencoded:
            schema: SellCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if not input or not input.get("card_id") or not input.get("price"):
        return (
            {"error": "Please provide all parameters for 'SellCardRequest' schema."},
            400,
        )

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    collection = db.getCollection(current_user, card)
    if not collection or collection.count <= 0:
        return ({"error": f"You does not own {card.name}"}, 404)

    # mark the card as available on the marked
    collection.is_marketed = True
    collection.price = input.get("price")
    db.session.add(collection)
    db.session.commit()

    return {"message": "Card placed on the market!"}


@app.route("/buy", methods=["POST"])
@token_required
def buy_card(current_user: UserModel):
    """Buy card from another user.
    ---
    post:
      tags:
        - Market
      summary: Buy card from another user.
      description: Buy card from another user.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: BuyCardRequest
          application/x-www-form-urlencoded:
            schema: BuyCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if not input or not input.get("seller_id") or not input.get("card_id"):
        return (
            {"error": "Please provide all parameters for 'BuyCardRequest' schema."},
            400,
        )
    
    # load seller user
    seller: UserModel = db.session.get(UserModel, input.get("seller_id"))
    if not seller:
        return ({"error": f"No user with id: {input.get('seller_id')}"}, 404)
    if seller.id == current_user.id:
        return ({"error": f"Cannot buy from yourself!"}, 400)

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    # load seller collection
    seller_collection = db.getCollection(seller, card)
    if not seller_collection or seller_collection.count <= 0:
        return ({"error": f"{seller.username} does not own {card.name}"}, 404)
    if not seller_collection.is_marketed:
        return ({"error": f"{seller.username} does not sell {card.name}"}, 400)

    # check buyer available funds
    if current_user.credits < seller_collection.price:
        return (
            {
                "error": f"You do not have enough credits to buy {card.name}. Available: {current_user.credits}, needed: {seller_collection.price}"
            },
            400,
        )

    # remove from seller collecton
    seller_collection.count -= 1
    if seller_collection.count <= 0:
        db.session.delete(seller_collection)
    else:
        db.session.add(seller_collection)

    # add to buyer collection
    buyer_collection = db.getCollection(current_user, card)
    if not buyer_collection:
        # create new buyer collection for this card
        buyer_collection = CollectionModel(count=1, price=100)
        buyer_collection.card = card
        buyer_collection.is_marketed = False
        current_user.collections.append(buyer_collection)
    else:
        buyer_collection.count += 1

    # funds transaction
    current_user.credits -= seller_collection.price
    seller.credits += seller_collection.price

    # finalize and commit
    db.session.add_all([current_user, seller])
    db.session.commit()

    return {"message": "Transaction is successfull!"}


@app.route("/cancel", methods=["POST"])
@token_required
def cancel_sell_card(current_user: UserModel):
    """Pull your card off the market.
    ---
    post:
      tags:
        - Market
      summary: Pull your card off the market.
      description: Pull your card off the market.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: CancelSellCardRequest
          application/x-www-form-urlencoded:
            schema: CancelSellCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if not input or not input.get("card_id"):
        return (
            {
                "error": "Please provide all parameters for 'CancelSellCardRequest' schema."
            },
            400,
        )

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    collection = db.getCollection(current_user, card)
    if not collection or collection.count <= 0:
        return ({"error": f"You do not own {card.name}"}, 404)

    # mark the card as unavailable on the marked
    collection.is_marketed = False
    db.session.add(collection)
    db.session.commit()

    return {"message": "Card pulled off the market!"}


@app.route("/admin/sell", methods=["POST"])
@token_required
@admin_required
def admin_sell_user_card(current_user: UserModel):
    """Sell card of a user.
    ---
    post:
      tags:
        - Admin
      summary: Sell card of a user.
      description: Sell card of a user.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: SellUserCardRequest
          application/x-www-form-urlencoded:
            schema: SellUserCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if (
        not input
        or not input.get("card_id")
        or not input.get("user_id")
        or not input.get("price")
    ):
        return (
            {
                "error": "Please provide all parameters for 'SellUserCardRequest' schema."
            },
            400,
        )

    # load user
    user: UserModel = db.session.get(UserModel, input.get("user_id"))
    if not user:
        return ({"error": f"No user with id: {input.get('user_id')}"}, 404)

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    collection = db.getCollection(user, card)
    if not collection or collection.count <= 0:
        return ({"error": f"{user.username} does not own {card.name}"}, 404)

    # mark the card as available on the marked
    collection.is_marketed = True
    collection.price = input.get("price")
    db.session.add(collection)
    db.session.commit()

    return {"message": "Card placed on the market!"}


@app.route("/admin/buy", methods=["POST"])
@token_required
@admin_required
def admin_buy_user_card(current_user: UserModel):
    """Buy card of a user for another user.
    ---
    post:
      tags:
        - Admin
      summary: Buy card of a user for another user.
      description: Buy card of a user for another user.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: BuyUserCardRequest
          application/x-www-form-urlencoded:
            schema: BuyUserCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if (
        not input
        or not input.get("buyer_id")
        or not input.get("seller_id")
        or not input.get("card_id")
    ):
        return (
            {"error": "Please provide all parameters for 'BuyUserCardRequest' schema."},
            400,
        )
    
    if(input.get("seller_id") == input.get("buyer_id")):
        return ({"error": f"Seller and buyer must be different users!"}, 400)

    # load buyer user
    buyer: UserModel = db.session.get(UserModel, input.get("buyer_id"))
    if not buyer:
        return ({"error": f"No user with id: {input.get('buyer_id')}"}, 404)

    # load seller user
    seller: UserModel = db.session.get(UserModel, input.get("seller_id"))
    if not seller:
        return ({"error": f"No user with id: {input.get('seller_id')}"}, 404)

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    # load seller collection
    seller_collection = db.getCollection(seller, card)
    if not seller_collection or seller_collection.count <= 0:
        return ({"error": f"{seller.username} does not own {card.name}"}, 404)
    if not seller_collection.is_marketed:
        return ({"error": f"{seller.username} does not sell {card.name}"}, 400)

    # check buyer available funds
    if buyer.credits < seller_collection.price:
        return (
            {
                "error": f"{buyer.username} has not enough credits to buy {card.name}. Available: {buyer.credits}, needed: {seller_collection.price}"
            },
            400,
        )

    # remove from seller collecton
    seller_collection.count -= 1
    if seller_collection.count <= 0:
        db.session.delete(seller_collection)
    else:
        db.session.add(seller_collection)

    # add to buyer collection
    buyer_collection = db.getCollection(buyer, card)
    if not buyer_collection:
        # create new buyer collection for this card
        buyer_collection = CollectionModel(count=1, price=100)
        buyer_collection.card = card
        buyer_collection.is_marketed = False
        buyer.collections.append(buyer_collection)
    else:
        buyer_collection.count += 1

    # funds transaction
    buyer.credits -= seller_collection.price
    seller.credits += seller_collection.price

    # finalize and commit
    db.session.add_all([buyer, seller])
    db.session.commit()

    return {"message": "Transaction is successfull!"}


@app.route("/admin/cancel", methods=["POST"])
@token_required
@admin_required
def admin_cancel_sell_user_card(current_user: UserModel):
    """Cancel selling card of a user.
    ---
    post:
      tags:
        - Admin
      summary: Cancel selling card of a user.
      description: Cancel selling card of a user.
      security:
        - token: []
      requestBody:
        content:
          application/json:
            schema: CancelSellUserCardRequest
          application/x-www-form-urlencoded:
            schema: CancelSellUserCardRequest
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: OkResponse
        400:
          description: Bad Request
          content:
            application/json:
              schema: ErrorResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        404:
          description: Not Found
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        input = request.json
    else:
        input = request.form

    #
    # Some validation
    #
    if not input or not input.get("card_id") or not input.get("user_id"):
        return (
            {
                "error": "Please provide all parameters for 'CancelSellUserCardRequest' schema."
            },
            400,
        )

    # load user
    user: UserModel = db.session.get(UserModel, input.get("user_id"))
    if not user:
        return ({"error": f"No user with id: {input.get('user_id')}"}, 404)

    # load card
    card: CardModel = db.session.get(CardModel, input.get("card_id"))
    if not card:
        return ({"error": f"No card with id: {input.get('card_id')}"}, 404)

    collection = db.getCollection(user, card)
    if not collection or collection.count <= 0:
        return ({"error": f"{user.username} does not own {card.name}"}, 404)

    # mark the card as unavailable on the marked
    collection.is_marketed = False
    db.session.add(collection)
    db.session.commit()

    return {"message": "Card pulled off the market!"}


@app.route("/admin/users", methods=["GET"])
@token_required
@admin_required
def admin_users(current_user: UserModel):
    """Get users.
    ---
    get:
      tags:
        - Admin
      summary: Get users.
      description: Get users.
      security:
        - token: []
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: UsersAdminResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    users = db.getAllUsers()

    return {
        "current": current_user.username,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "credits": user.credits,
                "collection": [
                    {
                        "card_id": c.card_id,
                        "name": c.card.name,
                        "count": c.count,
                        "url": c.card.url,
                        "price": c.price,
                        "is_marketed": c.is_marketed,
                    }
                    for c in user.collections
                ],
            }
            for user in users
        ],
    }


@app.route("/admin/cards", methods=["GET"])
@token_required
@admin_required
def admin_cards(current_user: UserModel):
    """Get cards.
    ---
    get:
      tags:
        - Admin
      summary: Get cards.
      description: Get cards.
      security:
        - token: []
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: CardsAdminResponse
        401:
          description: Unauthorized
          content:
            application/json:
              schema: ErrorResponse
        403:
          description: Forbidden
          content:
            application/json:
              schema: ErrorResponse
        500:
          description: Internal Server Error
          content:
            application/json:
              schema: ErrorResponse
    """
    cards = db.getAllCards()

    return {
        "cards": [
            {
                "name": card.name,
                "url": card.url,
            }
            for card in cards
        ],
    }


# add routes to openapi spec
with app.test_request_context():
    spec.path(view=auth)
    spec.path(view=signup)
    spec.path(view=my_user)
    spec.path(view=my_collection)
    spec.path(view=market)
    spec.path(view=sell_card)
    spec.path(view=buy_card)
    spec.path(view=cancel_sell_card)
    spec.path(view=admin_sell_user_card)
    spec.path(view=admin_buy_user_card)
    spec.path(view=admin_cancel_sell_user_card)
    spec.path(view=admin_users)
    spec.path(view=admin_cards)

# generate static openapi.yaml config file
openApiYaml = open("static/openapi.yaml", "w")
openApiYaml.write(spec.to_yaml())
openApiYaml.close()

# create Swagger UI page blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    "/api",
    "/static/openapi.yaml",
    config={"app_name": "TCG Game!"},
)

# register the swagger UI blueprint
app.register_blueprint(swaggerui_blueprint)
