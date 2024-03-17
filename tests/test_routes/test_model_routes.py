import hashlib
from flask import jsonify
import pytest
import json
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel


TEST_USER_NAME = "user"
TEST_USER_ROLE = "else"
TEST_USER_EMAIL = "user@test.com"
TEST_USER_PASSWORD = "StrongPassword123"
TEST_MODEL_REQUEST_DATA = {
    "name": "test-model",
    "nationalities": ["chinese", "else"],
}
TEST_MODEL_RESPONSE_DATA = {
    "name": "test-model",
    "nationalities": ["chinese", "else"],
    "accuracy": None,
    "scores": None,
    "isCustom": True,
    # creationTime: ... (not comparing because how?)
}


@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        
        # Create all tables if they don't exist
        # They will probably exist when you test locally and used the ``run_dev_db.sh`` script,
        # but they won't exist in the CI/CD runner therefore we call it here
        db.create_all()
        
        # Create a test user for which to test different CRUD operations
        # But if such this test user already exists, delete it and its questionnaire data
        test_user = User.query.filter_by(email=TEST_USER_EMAIL).first()
        if test_user:
            db.session.delete(test_user)

        test_model_id = hashlib.sha256(",".join(sorted(set(TEST_MODEL_REQUEST_DATA["nationalities"]))).encode()).hexdigest()[:20]
        test_model = Model.query.filter_by(id=test_model_id).first()
        if test_model:
            db.session.delete(test_model)

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    # Creates the test user and retrieves a JWT token to make /questionnaire requests with

    signup_data = {
        "name": TEST_USER_NAME,
        "email": TEST_USER_EMAIL,
        "role": TEST_USER_ROLE,
        "password": TEST_USER_PASSWORD,
        "consented": True
    }
    response = app.test_client().post("/signup", json=signup_data)
    assert response.status_code == 200

    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    response = app.test_client().post("/login", json=login_data)
    assert response.status_code == 200

    token = json.loads(response.data)["data"]["accessToken"]

    return app_context.test_client(), token


def test_add_model(test_client):
    test_client, token = test_client

    test_header = {
        "Authorization": f"Bearer {token}"
    }
    response = test_client.post("/models", json=TEST_MODEL_REQUEST_DATA, headers=test_header)

    # Get the test user ID by the email
    test_user_id = User.query.filter_by(email=TEST_USER_EMAIL).first().id

    expected_response_data = {
        "message": "Model added successfully."
    }
    assert response.status_code == 200
    assert UserToModel.query.filter_by(user_id=test_user_id).first() is not None
    assert json.loads(response.data) == expected_response_data

        
def test_get_models(test_client):
    test_client, token = test_client

    # Make GET request    
    test_header = {
        "Authorization": f"Bearer {token}"
    }
    response = test_client.get("/models", headers=test_header)
    
    expected_response_data = {
        "data": {
            "customModels": [TEST_MODEL_RESPONSE_DATA]
        },
        "message": "Model data received successfully."
    }

    response_data = json.loads(response.data)

    # Remove fields that are too difficult to check
    del response_data["data"]["customModels"][0]["creationTime"]
    del response_data["data"]["defaultModels"]

    assert response.status_code == 200
    assert response_data == expected_response_data


def test_delete_models(test_client):
    test_client, token = test_client

    # Make GET request
    test_header = {
        "Authorization": f"Bearer {token}"
    }
    test_body = {
        "names": [TEST_MODEL_REQUEST_DATA["name"]]
    }
    response = test_client.delete("/models", json=test_body, headers=test_header)
    
    expected_response_data = {
        "message": "Model(-s) deleted successfully."
    }
    deleted_model = UserToModel.query.filter_by(name=TEST_MODEL_REQUEST_DATA["name"]).first()
    
    assert deleted_model is None
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data

"""
def test_no_auth_questionnaire(test_client):
    # POSTing a questionnaire without providing a authentication token
    test_client, _ = test_client
    response = test_client.post("/questionnaire", json=TEST_QUESTIONNAIRE_DATA)

    assert response.status_code == 401"""