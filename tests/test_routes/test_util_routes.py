from flask import jsonify
import pytest
import json

from sqlalchemy import text
from utils import *
from app import app
from db.database import db
from db.tables import User


TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True
}

@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))
        db.session.commit()

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    # Creates the test user and retrieves a JWT token to make /models requests with
    response = app.test_client().post("/signup", json=TEST_USER)
    assert response.status_code == 200

    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = app.test_client().post("/login", json=login_data)
    assert response.status_code == 200

    token = json.loads(response.data)["data"]["accessToken"]

    return app_context.test_client(), token


def test_get_nationalities(test_client):
    test_client, _ = test_client

    response = test_client.get("/nationalities")

    expected_response_data = get_nationalities()
                              
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data