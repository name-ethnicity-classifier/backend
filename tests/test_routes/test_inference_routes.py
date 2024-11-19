import hashlib
import os
from unittest.mock import patch
import bcrypt
from flask import jsonify
from flask_jwt_extended import create_access_token
import pytest
import json
from pathlib import Path
from sqlalchemy import text
from schemas.inference_schema import InferenceDistributionResponseSchema, InferenceResponseSchema
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel


# Ensure this model configuration exist inside model_configuration/
DEFAULT_MODEL = {
    "public_name": "default-model",
    "nationalities": (classes := sorted(set(["chinese", "else"]))),
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False,
    "is_public": True,
    "id": generate_model_id(classes),
}

TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "verified": True,
    "consented": True
}
TEST_USER_ID = 1

# Ensure this model configuration exist inside model_configuration/
CUSTOM_MODEL = {
    "public_name": None,
    "nationalities": (classes := sorted(set(["japanese", "else"]))),
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False,
    "is_public": False,
    "id": generate_model_id(classes),
}
USER_TO_MODEL = {
    "model_id": CUSTOM_MODEL["id"],
    "user_id": TEST_USER_ID,
    "request_count": 0,
    "name": "custom-model"
}
USER_TO_DEFAULT_MODEL = {
    "model_id": DEFAULT_MODEL["id"],
    "user_id": TEST_USER_ID,
    "request_count": 0,
    "name": "custom-model-same-as-default"
}


@pytest.fixture(scope="function")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))

        # Add a default model, the test user, a custom trained model and
        # a custom model that points to the default model because it has the same classes
        db.session.add(Model(**DEFAULT_MODEL))
        db.session.add(User(**TEST_USER))
        db.session.add(Model(**CUSTOM_MODEL))
        db.session.add(UserToModel(**USER_TO_MODEL))
        db.session.add(UserToModel(**USER_TO_DEFAULT_MODEL))
        db.session.commit()

        if not Path(f"./model_configurations/{DEFAULT_MODEL['id']}").exists():
            raise FileNotFoundError(f"For this test, the ./model_configurations/ folder is expected to have a folder with the 'model_id' ({DEFAULT_MODEL['id']}) as name! It must contain a valid model configuration with a .pt file, etc.")

        if not Path(f"./model_configurations/{CUSTOM_MODEL['id']}").exists():
            raise FileNotFoundError(f"For this test, the ./model_configurations/ folder is expected to have a folder with the 'model_id' ({CUSTOM_MODEL['id']}) as name! It must contain a valid model configuration with a .pt file, etc.")

        yield app


@pytest.fixture(scope="function")
def test_client(app_context):
    client = app.test_client()
    return client


@pytest.fixture(scope="function")
def authenticated_client(test_client):
    """Mocks user authentication for tests requiring it."""
    with patch("flask_jwt_extended.get_jwt_identity") as mock_identity:
        mock_identity.return_value = TEST_USER_ID

        with app.test_request_context():
            token = create_access_token(identity=TEST_USER_ID)
        test_client.token = token
        yield test_client


@pytest.mark.it("should respond with correct predictions when classfiying using a custom model")
def test_custom_model_classification(authenticated_client):
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
            "getDistribution": False
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    classification_result = json.loads(response.data)

    InferenceResponseSchema(**classification_result)

    assert response.status_code == 200
    classified_ethnicities = {name: prediction[0] for name, prediction in classification_result.items()}
    assert classified_ethnicities == {"cixin liu": "japanese", "peter schmidt": "else"}

    assert Model.query.filter_by(id=CUSTOM_MODEL["id"]).first().request_count == 1
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, name=USER_TO_MODEL["name"]).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().names_classified == 2


@pytest.mark.it("should respond with a output distribution for all classes when classfiying using 'getDistribution' set to 'True'")
def test_custom_model_classification_distribution(authenticated_client):
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
            "getDistribution": True
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    classification_result = json.loads(response.data)

    InferenceDistributionResponseSchema(**classification_result)
    assert response.status_code == 200
    
    # Get the ethnicites with the highest confidence to check if they match expected predictions
    top_one_ethnicities = {}
    for name in classification_result:
        ethnicity_dist = classification_result[name]
        top_one_ethnicities[name] = max(ethnicity_dist, key=ethnicity_dist.get)

    assert top_one_ethnicities == {"cixin liu": "japanese", "peter schmidt": "else"}
    assert Model.query.filter_by(id=CUSTOM_MODEL["id"]).first().request_count == 1
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, name=USER_TO_MODEL["name"]).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().names_classified == 2


@pytest.mark.it("should respond with correct predictions when classfiying using a custom model which points to a default model with same classes")
def test_custom_same_as_default_model_classification(authenticated_client):
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_DEFAULT_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
            "getDistribution": False
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    classification_result = json.loads(response.data)

    InferenceResponseSchema(**classification_result)

    assert response.status_code == 200
    classified_ethnicities = {name: prediction[0] for name, prediction in classification_result.items()}
    assert classified_ethnicities == {"cixin liu": "chinese", "peter schmidt": "else"}

    assert Model.query.filter_by(id=DEFAULT_MODEL["id"]).first().request_count == 1
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, name=USER_TO_DEFAULT_MODEL["name"]).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().names_classified == 2


@pytest.mark.it("should respond with correct predictions when classfiying using a default model")
def test_default_model_classification(authenticated_client):
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": DEFAULT_MODEL["public_name"],
            "names": ["peter schmidt", "cixin liu"],
            "getDistribution": False
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    classification_result = json.loads(response.data)

    InferenceResponseSchema(**classification_result)

    assert response.status_code == 200
    classified_ethnicities = {name: prediction[0] for name, prediction in classification_result.items()}
    assert classified_ethnicities == {"cixin liu": "chinese", "peter schmidt": "else"}

    assert Model.query.filter_by(id=DEFAULT_MODEL["id"]).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().request_count == 1
    assert User.query.filter_by(id=TEST_USER_ID).first().names_classified == 2