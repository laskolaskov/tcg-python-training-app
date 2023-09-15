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
from models import UserModel

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
            return jsonify({"message": "Token is missing !!"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(jwt=token, key=secret_key, algorithms="HS256")
            current_user: UserModel = db.getUserByName(data["public_id"])
        except:
            return jsonify({"message": "Token is invalid !!"}), 401
        # returns the current logged in users context to the routes
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
      description: Create new access token for user
      summary: Get access token
      requestBody:
        content:
          application/json:
            schema: UserCredentials
          application/x-www-form-urlencoded:
            schema: UserCredentials
      content: application/json
      responses:
        200:
          content:
            application/json:
              schema: TokenResponse
        401:
          content:
            application/json:
              schema: ErrorResponse
        403:
          content:
            application/json:
              schema: ErrorResponse
        500:
          content:
            application/json:
              schema: ErrorResponse
    """
    if request.content_type == "application/json":
        auth = request.json
    else:
        auth = request.form

    if not auth or not auth.get("username") or not auth.get("password"):
        # returns 401 if any email or / and password is missing
        return ({"error": "Please provide user credentials"}, 401)

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
      description: Create new user account with e-mail and password
      summary: Create new user
      requestBody:
        content:
          application/json:
            schema: SignupRequest
          application/x-www-form-urlencoded:
            schema: SignupRequest
      responses:
        200:
          content:
            application/json:
              schema: UserCreatedResponse
        400:
          content:
            application/json:
              schema: ErrorResponse
    """

    if request.content_type == "application/json":
        data = request.json
    else:
        data = request.form

    if not data or not data.get("username") or not data.get("password"):
        # returns 401 if any email or / and password is missing
        return ({"error": "Please provide username and password"}, 401)

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
      security:
        - token: []
      responses:
        200:
          content:
            application/json:
              schema: CollectionResponse
    """
    c = []
    for collection in current_user.collections:
        c.append(
            {
                "name": collection.card.name,
                "url": collection.card.url,
                "count": collection.count,
                "price": collection.price,
                "is_marketed": collection.is_marketed,
            }
        )

    return {"owner": current_user.username, "collection": c}


@app.route("/my/user", methods=["GET"])
@token_required
def my_user(current_user: UserModel):
    """My user information.
    ---
    get:
      tags:
        - My Data
      security:
        - token: []
      responses:
        200:
          content:
            application/json:
              schema: UserResponse
    """
    return {
        "name": current_user.username,
        "credits": current_user.credits,
        "cards": len(current_user.collections),
    }


@app.route("/sell/card/<id>/price/<price>", methods=["POST"])
def sell_card():
    """Authenticate.
    ---
    post:
      tags:
        - Authenticate
      description: Create new access token for user
      summary: Get access token
      requestBody:
        content:
          application/json:
            schema: UserCredentials
          application/x-www-form-urlencoded:
            schema: UserCredentials
      content: application/json
      responses:
        200:
          content:
            application/json:
              schema: TokenResponse
        401:
          content:
            application/json:
              schema: ErrorResponse
        403:
          content:
            application/json:
              schema: ErrorResponse
        500:
          content:
            application/json:
              schema: ErrorResponse
    """


# add routes to openapi spec
with app.test_request_context():
    spec.path(view=auth)
    spec.path(view=signup)
    spec.path(view=my_user)
    spec.path(view=my_collection)

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
