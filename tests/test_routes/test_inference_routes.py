import hashlib
from flask import jsonify
import pytest
import json
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel


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

# Resulting model id will be: cf58c0536d2ab4fbd6a6
# Therefore a model configuration folder ./model_configurations/cf58c0536d2ab4fbd6a6 is expected to exist that contains
# a model to classify into chinese and else
TEST_MODEL_ID = hashlib.sha256(",".join(sorted(set(TEST_MODEL_DATA["nationalities"]))).encode()).hexdigest()[:20]

TEST_CLASSIFICATION_DATA = {
    "modelName": TEST_MODEL_DATA["name"],
    "names": ["peter schmidt", "cixin liu"],
    "getDistribution": False
}
TEST_EXPECTED_PREDICTIONS = {"cixin liu": "chinese", "peter schmidt": "else"}


@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        
        # Create all tables if they don't exist
        # They will probably exist when you test locally and used the ``run_dev_db.sh`` script,
        # but they won't exist in the CI/CD runner therefore we call it here
        db.create_all()
        
        # Create a test user for which to test different CRUD operations
        # But if such this test user already exists, delete it and its model data
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
    # Creates the test user and retrieves a JWT token to make /models requests with
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
    classifaction_result = json.loads(response.data)
    # Format: { "name surname": ["nationality", 90.1], "name surname": ["nationality", 90.1]}

    assert response.status_code == 200
    assert set(classifaction_result.keys()) == set(TEST_CLASSIFICATION_DATA["names"])

    classified_ethnicities = {name: prediction[0] for name, prediction in classifaction_result.items()}
    assert classified_ethnicities == TEST_EXPECTED_PREDICTIONS

    # Check if the request counter got incremented from 0 to 1
    user_id = User.query.filter_by(email=TEST_USER_DATA["email"]).first().id
    request_count = UserToModel.query.filter_by(user_id=user_id, name=TEST_MODEL_DATA["name"]).first().request_count
    assert request_count == 1


def test_get_classification_distribution(test_client):
    test_client, token = test_client

    test_header = {
        "Authorization": f"Bearer {token}"
    }

    TEST_CLASSIFICATION_DATA["getDistribution"] = True

    response = test_client.post("/classify", json=TEST_CLASSIFICATION_DATA, headers=test_header)
    classifaction_result = json.loads(response.data)
    # Format: ["name": {"nationality1": 90.0, nationality2: 10.0}, "name": {"nationality1": 10.0, "nationality2": 90.0}]

    assert response.status_code == 200
    assert set(classifaction_result.keys()) == set(TEST_CLASSIFICATION_DATA["names"])
    assert set(classifaction_result[TEST_CLASSIFICATION_DATA["names"][0]].keys()) == set(["else", "chinese"])
    
    # Get the ethnicites with the highest confidence
    top_one_ethnicities = {}
    for name in classifaction_result:
        ethnicity_dist = classifaction_result[name]
        top_one_ethnicities[name] = max(ethnicity_dist, key=ethnicity_dist.get)

    assert top_one_ethnicities == TEST_EXPECTED_PREDICTIONS
