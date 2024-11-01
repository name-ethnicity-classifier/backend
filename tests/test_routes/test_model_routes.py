import hashlib
from flask import jsonify
import pytest
import json
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel
from sqlalchemy import text


DEFAULT_MODEL = {
    "public_name": "test-default-model",
    "nationalities": ["chinese", "else"],
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False
}
CUSTOM_MODEL = {
    "name": "test-custom-model",
    "nationalities": ["german", "else"],
    "accuracy": None,
    "scores": None,
    "is_trained": False,
    "is_grouped": False,
    "public_name": None
}

USER_DATA = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True
}
"""TEST_DEFAULT_MODEL_REQUEST_DATA = {
    "name": DEFAULT_MODEL["name"],
    "nationalities": DEFAULT_MODEL["nationalities"]   # already exist as default model
}
TEST_NEW_MODEL_REQUEST_DATA = {
    "name": "test-model-new",
    "nationalities": ["dutch", "german"]   # doesn't exist as default model
}
TEST_CUSTOM_MODEL_RESPONSE_DATA = {
    "name": "test-model-new",
    "nationalities": ["chinese", "else"],
    "accuracy": None,
    "scores": None,
    "isPublic": False,
    # creationTime: ... (not comparing because how?)
}"""

GET_MODELS_RESPONSE = {
    "customModels": [{
        "name": CUSTOM_MODEL["name"],
        "nationalities": sorted(CUSTOM_MODEL["nationalities"]),
        "accuracy": CUSTOM_MODEL["accuracy"],
        "scores": CUSTOM_MODEL["scores"],
        "isPublic": False
    }],
    "defaultModels": [{
        "name": DEFAULT_MODEL["public_name"],
        "nationalities": sorted(DEFAULT_MODEL["nationalities"]),
        "accuracy": DEFAULT_MODEL["accuracy"],
        "scores": DEFAULT_MODEL["scores"],
        "isPublic": True
    }]
}



@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        db.drop_all()
    
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))

        new_model = Model(
            id=generate_model_id(DEFAULT_MODEL["nationalities"]),
            public_name=DEFAULT_MODEL["public_name"],
            nationalities=sorted(set(DEFAULT_MODEL["nationalities"])),
            accuracy=DEFAULT_MODEL["accuracy"],
            scores=DEFAULT_MODEL["scores"],
            is_trained=DEFAULT_MODEL["is_trained"],
            is_public=True,
            is_grouped=DEFAULT_MODEL["is_grouped"]
        )
        db.session.add(new_model)

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    response = app.test_client().post("/signup", json=USER_DATA)
    assert response.status_code == 200

    login_data = {
        "email": USER_DATA["email"],
        "password": USER_DATA["password"]
    }
    response = app.test_client().post("/login", json=login_data)
    assert response.status_code == 200

    return app_context.test_client(), json.loads(response.data)["data"]["accessToken"]


def test_add_new_model_to_user(test_client):
    test_client, token = test_client
   
    response = test_client.post(
        "/models",
        json={"name": CUSTOM_MODEL["name"], "nationalities": CUSTOM_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )

    test_user_id = User.query.filter_by(email=USER_DATA["email"]).first().id
    model_id = generate_model_id(CUSTOM_MODEL["nationalities"])

    expected_response_data = {
        "message": "Model added successfully."
    }
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


def test_add_existing_model_to_user(test_client):
    test_client, token = test_client

    response = test_client.post(
        "/models",
        json={"name": DEFAULT_MODEL["public_name"], "nationalities": DEFAULT_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )

    test_user_id = User.query.filter_by(email=USER_DATA["email"]).first().id

    expected_response_data = {
        "message": "Model added successfully."
    }
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id).first() is not None

        
def test_get_models(test_client):
    test_client, token = test_client

    # Make GET request    
    test_header = {
        "Authorization": f"Bearer {token}"
    }
    response = test_client.get("/models", headers=test_header)
    
    expected_response_data = {
        "data": GET_MODELS_RESPONSE,
        "message": "Model data received successfully."
    }

    response_data = json.loads(response.data)

    # Remove fields that are too difficult to check
    del response_data["data"]["customModels"][0]["creationTime"]
    del response_data["data"]["defaultModels"][0]["creationTime"]

    assert response.status_code == 200
    assert response_data == expected_response_data


"""def test_delete_models(test_client):
    test_client, token = test_client

    # Make GET request
    test_header = {
        "Authorization": f"Bearer {token}"
    }
    test_body = {
        "names": [TEST_EXISTING_MODEL_REQUEST_DATA["name"]]
    }
    response = test_client.delete("/models", json=test_body, headers=test_header)
    
    expected_response_data = {
        "message": "Model(-s) deleted successfully."
    }
    deleted_model = UserToModel.query.filter_by(name=TEST_EXISTING_MODEL_REQUEST_DATA["name"]).first()
    
    assert deleted_model is None
    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
"""