from datetime import timedelta
import json
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from flask_spec_gen import openapi_generator as og

from db.database import db
from routes.model_routes import model_routes
from routes.user_routes import user_routes
from routes.util_routes import util_routes
from routes.inference_routes import inference_routes
from globals import VERSION

load_dotenv()

app = Flask(__name__)

db_host = os.environ.get("POSTGRES_HOST")
db_port = os.environ.get("POSTGRES_PORT")
db_name = os.environ.get("POSTGRES_DB")
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_host}:{db_port}/{db_name}?user={db_user}&password={db_password}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=int(os.environ.get("JWT_EXPIRATION_DAYS")))

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

app.config["API_VERSION"] = VERSION

with open("./data/config.json", "r") as f:
    openapi_base_config = json.load(f)

openapi_generator = og.OpenAPIGenerator(app, openapi_base_config)

CORS(app)
JWTManager(app)
db.init_app(app)

@app.route("/")
def index():
    return json.dumps({"status": "OK"})

app.logger.setLevel(logging.INFO)
app.register_blueprint(user_routes)
app.register_blueprint(model_routes)
app.register_blueprint(inference_routes)
app.register_blueprint(util_routes)

openapi_generator.generate()

if __name__ == "__main__":
    app.run()
