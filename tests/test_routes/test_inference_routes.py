import hashlib
import os
import bcrypt
from flask import jsonify
import pytest
import json
from pathlib import Path
from sqlalchemy import text
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel


TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True,
    "verified": True
}
CUSTOM_MODEL = {
    "name": "test-custom-model",
    "nationalities": ["chinese", "else"],
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False,
    "is_public": False
}
TEST_CLASSIFICATION_DATA = {
    "modelName": CUSTOM_MODEL["name"],
    "names": ["peter schmidt", "cixin liu"],
    "getDistribution": False
}
TEST_EXPECTED_PREDICTIONS = {"cixin liu": "chinese", "peter schmidt": "else"}


@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))

        # Add user with whom to test the inference
        existing_test_user = User(
            name=TEST_USER["name"],
            email=TEST_USER["email"],
            role=TEST_USER["role"],
            password=bcrypt.hashpw(TEST_USER["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            verified=TEST_USER["verified"],
            consented=TEST_USER["consented"]
        )
        db.session.add(existing_test_user)
        db.session.commit()

        # Add a custom model with classes [chinese, else]
        model_id = generate_model_id(CUSTOM_MODEL["nationalities"])

        if not Path(f"./model_configurations/{model_id}").exists():
            raise FileNotFoundError(f"For this test, the ./model_configurations/ folder is expected to have a folder with the 'model_id' ({model_id}) as name! It must contain a valid model configuration with a .pt file, etc.")

        existing_model = Model(
            id=model_id,
            public_name=CUSTOM_MODEL["name"],
            nationalities=sorted(set(CUSTOM_MODEL["nationalities"])),
            accuracy=CUSTOM_MODEL["accuracy"],
            scores=CUSTOM_MODEL["scores"],
            is_trained=CUSTOM_MODEL["is_trained"],
            is_grouped=CUSTOM_MODEL["is_grouped"],
            is_public=CUSTOM_MODEL["is_public"]
        )
        db.session.add(existing_model)
        db.session.commit()

        user_to_model_link = UserToModel(
            model_id=existing_model.id,
            user_id=existing_test_user.id,
            request_count=0,
            name=CUSTOM_MODEL["name"]
        )
        db.session.add(user_to_model_link)
        db.session.commit()

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = app.test_client().post("/login", json=login_data)

    assert response.status_code == 200

    return app_context.test_client(), json.loads(response.data)["data"]["accessToken"]


def test_classification(test_client):
    test_client, token = test_client

    response = test_client.post(
        "/classify",
        json=TEST_CLASSIFICATION_DATA,
        headers={"Authorization": f"Bearer {token}"}
    )
    classifaction_result = json.loads(response.data)
    # Schema: { <name: str>: [<predicted class: str>, <confidence: float>], ... }

    assert response.status_code == 200
    classified_ethnicities = {name: prediction[0] for name, prediction in classifaction_result.items()}
    assert classified_ethnicities == TEST_EXPECTED_PREDICTIONS

    # Check if the request counter got incremented from 0 to 1
    user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    request_count = UserToModel.query.filter_by(user_id=user_id, name=CUSTOM_MODEL["name"]).first().request_count
    assert request_count == 1


def test_get_classification_distribution(test_client):
    test_client, token = test_client

    test_header = {
        "Authorization": f"Bearer {token}"
    }

    TEST_CLASSIFICATION_DATA["getDistribution"] = True

    response = test_client.post("/classify", json=TEST_CLASSIFICATION_DATA, headers=test_header)
    classifaction_result = json.loads(response.data)
    # Schema: { <name: str>: {<class 1: str>: <confidence: float>, <class 2: str>: <confidcence: float>}, ... }

    assert response.status_code == 200
    
    # Get the ethnicites with the highest confidence to check if they match expected predictions
    top_one_ethnicities = {}
    for name in classifaction_result:
        ethnicity_dist = classifaction_result[name]
        top_one_ethnicities[name] = max(ethnicity_dist, key=ethnicity_dist.get)

    assert top_one_ethnicities == TEST_EXPECTED_PREDICTIONS


def test_classification_with_default_model(test_client):
    test_client, token = test_client


    # TODO