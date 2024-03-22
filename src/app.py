from datetime import timedelta
import json
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from db.database import db
from routes.model_routes import model_routes
from routes.authentication_routes import authentication_routes
from routes.util_routes import util_routes

load_dotenv()


db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

app = Flask(__name__)

postgres_uri = f"postgresql://{db_host}:{db_port}/{db_name}?user={db_user}&password={db_password}"
app.config["SQLALCHEMY_DATABASE_URI"] = postgres_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=int(os.environ.get("JWT_EXPIRATION_DAYS")))

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

@app.route("/")
def index():
    return json.dumps({"status": "OK"})

app.logger.setLevel(logging.INFO)
app.register_blueprint(authentication_routes)
app.register_blueprint(model_routes)
app.register_blueprint(util_routes)


if __name__ == "__main__":
    app.run()
