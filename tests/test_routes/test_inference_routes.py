from datetime import timedelta
import os
from unittest.mock import patch
from flask import current_app
from flask_jwt_extended import create_access_token
import pytest
import json
from pathlib import Path
from sqlalchemy import text
from schemas.inference_schema import InferenceDistributionResponseSchema, InferenceResponseSchema
from utils import *
from app import app
from db.database import db
from db.tables import AccessLevel, User, Model, UserQuota, UserToModel


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
    "consented": True,
    "usage_description": "Lorem Ipsum" * 20,
    "access": AccessLevel.FULL.value,
    "verified": True
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


@pytest.fixture
def mock_max_names(app_context):
    max_names = 10
    with app.app_context():
        with patch.dict(current_app.config, {"MAX_NAMES": max_names}, clear=False):
            yield max_names


@pytest.fixture
def mock_daily_quota(app_context):
    daily_quota = 10
    with app.app_context():
        with patch.dict(current_app.config, {"DAILY_QUOTA": daily_quota}, clear=False):
            yield daily_quota


@pytest.mark.it("should respond with correct predictions when classfiying using a custom model")
def test_custom_model_classification(authenticated_client):
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"]
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


@pytest.mark.it("should respond with a output distribution for all classes when doing distribution classification")
def test_custom_model_classification_distribution(authenticated_client):
    response = authenticated_client.post(
        "/classify-distribution",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
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


@pytest.mark.it("should fail to do classification with restricted access")
def test_classification_with_restricted_access(authenticated_client):
    user = User.query.filter_by(id=TEST_USER_ID).first()
    user.access = AccessLevel.RESTRICTED.value

    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 403
    assert json.loads(response.data)["errorCode"] == "RESTRICTED_ACCESS"


@pytest.mark.it("should fail to do distribution classification with restricted access")
def test_classification_distribution_with_restricted_access(authenticated_client):
    user = User.query.filter_by(id=TEST_USER_ID).first()
    user.access = AccessLevel.RESTRICTED.value

    response = authenticated_client.post(
        "/classify-distribution",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt", "cixin liu"],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 403
    assert json.loads(response.data)["errorCode"] == "RESTRICTED_ACCESS"


@pytest.mark.it("should fail to do classification when requesting too many names")
def test_classification_with_too_many_names(mock_max_names, authenticated_client):
    max_names = mock_max_names

    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(max_names + 1)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 405
    assert json.loads(response.data)["errorCode"] == "TOO_MANY_NAMES"


@pytest.mark.it("should fail to do distribution classification when requesting too many names")
def test_classification_distribution_with_too_many_names(mock_max_names, authenticated_client):
    max_names = mock_max_names

    response = authenticated_client.post(
        "/classify-distribution",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(max_names + 1)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 405
    assert json.loads(response.data)["errorCode"] == "TOO_MANY_NAMES"


@pytest.mark.it("should fail to do classification when exceeding quota")
def test_classification_with_exceeded_quota(mock_daily_quota, authenticated_client):
    first_request_name_amount = mock_daily_quota // 2    # reaching 50% of daily quota
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(first_request_name_amount)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    assert response.status_code == 200

    second_request_name_amount = mock_daily_quota    # reaching 150% of daily quota
    response = authenticated_client.post(
        "/classify-distribution",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(second_request_name_amount)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 405
    assert json.loads(response.data)["errorCode"] == "QUOTA_EXCEEDED"


@pytest.mark.it("should reset daily quota when classifying over different days")
def test_classification_after_quota_resets(mock_daily_quota, authenticated_client):
    first_request_name_amount = mock_daily_quota // 2    # reaching 50% of daily quota
    response = authenticated_client.post(
        "/classify",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(first_request_name_amount)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    assert response.status_code == 200
    current_user_quota = UserQuota.query.filter_by(user_id=TEST_USER_ID).first()
    current_user_quota.last_updated -= timedelta(days=1)    # change date to yesterday

    # And in the very next morning... :)
    second_request_name_amount = mock_daily_quota    # reaching 100% of daily quota
    response = authenticated_client.post(
        "/classify-distribution",
        json={
            "modelName": USER_TO_MODEL["name"],
            "names": ["peter schmidt" for _ in range(second_request_name_amount)],
        },
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 200
