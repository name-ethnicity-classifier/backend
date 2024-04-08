import hashlib
from flask import jsonify
import pytest
import json
from utils import *
from app import app
from db.database import db
from db.tables import User, Model


TEST_USER_DATA = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True
}
TEST_MODEL_DATA = {
    "name": "test-model",
    "nationalities": ["chinese", "else"],
}
TEST_MODEL_ID = hashlib.sha256(",".join(sorted(set(TEST_MODEL_DATA["nationalities"]))).encode()).hexdigest()[:20]
TEST_CLASSIFICATION_DATA = {
    "modelName": TEST_MODEL_DATA["name"],
    "names": ["peter schmidt", "cixin liu"],
    "getDistribution": False
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
        test_user = User.query.filter_by(email=TEST_USER_DATA["email"]).first()
        if test_user:
            db.session.delete(test_user)
    
        # Add model to database
        test_model = Model.query.filter_by(id=TEST_MODEL_ID).first()
        if test_model:
            db.session.delete(test_model)

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    # Creates the test user and retrieves a JWT token to make /questionnaire requests with
    response = app.test_client().post("/signup", json=TEST_USER_DATA)
    assert response.status_code == 200

    login_data = {
        "email": TEST_USER_DATA["email"],
        "password": TEST_USER_DATA["password"]
    }
    response = app.test_client().post("/login", json=login_data)
    assert response.status_code == 200

    token = json.loads(response.data)["data"]["accessToken"]

    # Add test model for user
    test_header = {
        "Authorization": f"Bearer {token}"
    }
    response = app.test_client().post("/models", json=TEST_MODEL_DATA, headers=test_header)
    assert response.status_code == 200

    return app_context.test_client(), token


def test_classification(test_client):
    test_client, token = test_client

    test_header = {
        "Authorization": f"Bearer {token}"
    }
    response = test_client.post("/classify", json=TEST_CLASSIFICATION_DATA, headers=test_header)

    assert response.status_code == 200
    # assert json.loads(response.data) == expected_response_data

     