from flask import Flask
from flask import abort, redirect, url_for, request
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_plugins.webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields
from flask_swagger_ui import get_swaggerui_blueprint
from db import db_test


# Create an APISpec
spec = APISpec(
    title="TCG Game!",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


class TestSchema(Schema):
    id = fields.Int()
    content = fields.Str()


app = Flask(__name__)


@app.route("/")
def index():
    return redirect("/api")


@app.route("/test/<id>/<content>")
def test(id, content):
    """Gist detail view.
    ---
    get:
      parameters:
      - in: path
        schema: TestSchema
      responses:
        200:
          content:
            application/json:
              schema: TestSchema
    """
    # return "<h1>Test</h1>"
    return f"<h1>Post {id} - {content}</h1>"


@app.route("/test/db")
def db_test_ep():
    """Gist detail view.
    ---
    get:
      responses:
        200:
          content:
            application/json:
              schema: TestSchema
    """
    # return "<h1>Test</h1>"
    return f"<h1>DB: {db_test()}</h1>"


# add to openapi spec
with app.test_request_context():
    spec.path(view=test)
    spec.path(view=db_test_ep)

# generate static openapi.yaml config file
openApiYaml = open("static/openapi.yaml", "w")
openApiYaml.write(spec.to_yaml())
openApiYaml.close()

# swagger UI config
SWAGGER_URL = "/api"
API_URL = "/static/openapi.yaml"

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Test application"},
)

# register the swagger UI blueprint
app.register_blueprint(swaggerui_blueprint)

# run application
app.run()
