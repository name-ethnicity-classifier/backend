from flask import jsonify
import pytest
import json
from utils import *
from app import app
from db.database import db
from db.tables import User


TEST_USER_DATA = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True
}


@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        
        # Create all tables if they don't exist
        # They will probably exist when you test locally and used the ``run_dev_db.sh`` script,
        # but they won't exist in the CI/CD runner therefore we call it here
        db.create_all()
        
        # Create a test user for which to test different CRUD operations
        # But if this test user already exists, delete it and its questionnaire data
        test_user = User.query.filter_by(email=TEST_USER_DATA["email"]).first()
        if test_user:
            db.session.delete(test_user)

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    return app_context.test_client()


def test_signup_user(test_client):
    response = test_client.post("/signup", json=TEST_USER_DATA)

    # Check that the response status code is 200 (successful registration)
    assert response.status_code == 200
    assert User.query.filter_by(email=TEST_USER_DATA["email"]).first() is not None


def test_login_user(test_client):
    login_data = {
        "email": TEST_USER_DATA["email"],
        "password": TEST_USER_DATA["password"]
    }

    response = test_client.post("/login", json=login_data)

    # Check that the response status code is 200 (successful login)
    assert response.status_code == 200
    assert "accessToken" in json.loads(response.data)["data"]


def test_login_user_fail(test_client):
    # Not existing user
    login_data = {
        "email": "doesnt@exist.com",
        "password": "password"
    }

    response = test_client.post("/login", json=login_data)

    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "AUTHENTICATION_FAILED"

    # Invalid login request data (name instead of email)
    login_data = {
        "name": TEST_USER_DATA["name"],
        "password": TEST_USER_DATA["password"]
    }

    response = test_client.post("/login", json=login_data)

    assert response.status_code == 400
    assert json.loads(response.data)["errorCode"] == "INVALID_LOGIN_DATA"
