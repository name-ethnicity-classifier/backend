import datetime
import hashlib
from flask import jsonify
import pytest
import json
from schemas.model_schema import GetModelsResponseSchema, N2EModel
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
EXISTING_TEST_USER = {
    "name": "existing-test-user",
    "email": "existing.user@test.com",
    "role": "student",
    "password": "Hashedpassword123",
    "verified": True,
    "consented": True
}
EXISTING_CUSTOM_MODEL = {
    "name": "existing-custom-model",
    "nationalities": ["else", "japanese"],
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False
}
TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "verified": True,
    "consented": True
}
CUSTOM_MODEL = {
    "name": "custom-model",
    "nationalities": ["else", "german"],
    "accuracy": None,
    "scores": None,
    "is_trained": False,
    "is_grouped": False,
    "public_name": None
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
            is_grouped=DEFAULT_MODEL["is_grouped"],
            is_public=True
        )
        db.session.add(new_model)
        db.session.commit()

        existing_test_user = User(
            name=EXISTING_TEST_USER["name"],
            email=EXISTING_TEST_USER["email"],
            role=EXISTING_TEST_USER["role"],
            password=EXISTING_TEST_USER["password"],
            verified=EXISTING_TEST_USER["verified"],
            consented=EXISTING_TEST_USER["consented"]
        )
        db.session.add(existing_test_user)
        db.session.commit()

        # Generate an ID for the model (using a hash for example purposes)
        model_id = generate_model_id(EXISTING_CUSTOM_MODEL["nationalities"])

        # Create a test model
        test_model = Model(
            id=model_id,
            nationalities=EXISTING_CUSTOM_MODEL["nationalities"],
            accuracy=95.5,
            scores=EXISTING_CUSTOM_MODEL["scores"],
            is_trained=True,
            is_grouped=False,
            public_name=None,
            is_public=False
        )
        db.session.add(test_model)

        # Link the user and model via UserToModel
        user_to_model_link = UserToModel(
            model_id=test_model.id,
            user_id=existing_test_user.id,
            request_count=0,
            name=EXISTING_CUSTOM_MODEL["name"]
        )
        db.session.add(user_to_model_link)
        db.session.commit()

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    response = app.test_client().post("/signup", json=TEST_USER)
    assert response.status_code == 200

    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = app.test_client().post("/login", json=login_data)
    assert response.status_code == 200

    return app_context.test_client(), json.loads(response.data)["data"]["accessToken"]


@pytest.mark.order(1)
@pytest.mark.it("should add a new model and user-to-model entry when user creates custom model")
def test_add_custom_model(test_client):
    test_client, token = test_client
    response = test_client.post(
        "/models",
        json={"name": CUSTOM_MODEL["name"], "nationalities": CUSTOM_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    test_user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    model_id = generate_model_id(CUSTOM_MODEL["nationalities"])
    expected_response_data = {"message": "Model added successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id, model_id=model_id, name=CUSTOM_MODEL["name"]).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.order(2)
@pytest.mark.it("should add a new model when the user already has a model trained on same nationalities")
def test_add_custom_model_with_same_classes(test_client):
    test_client, token = test_client

    new_model_name = "custom-model-2"

    response = test_client.post(
        "/models",
        json={"name": new_model_name, "nationalities": CUSTOM_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    test_user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    model_id = generate_model_id(CUSTOM_MODEL["nationalities"])
    expected_response_data = {"message": "Model added successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id, model_id=model_id, name=new_model_name).first() is not None


@pytest.mark.order(3)
@pytest.mark.it("should add a custom model when there already is a default model trained on same nationalities")
def test_add_custom_model_with_same_classes_as_default_model(test_client):
    test_client, token = test_client

    new_model_name = "custom-model-3"

    response = test_client.post(
        "/models",
        json={"name": new_model_name, "nationalities": DEFAULT_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    test_user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    model_id = generate_model_id(DEFAULT_MODEL["nationalities"])
    expected_response_data = {"message": "Model added successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id, model_id=model_id, name=new_model_name).first() is not None


@pytest.mark.order(4)
@pytest.mark.it("should fail to add a custom model when the user already has a model with the same name")
def test_add_custom_model_with_same_name(test_client):
    test_client, token = test_client
    response = test_client.post(
        "/models",
        json={"name": CUSTOM_MODEL["name"], "nationalities": ["japanese", "dutch"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_EXISTS"


@pytest.mark.order(5)
@pytest.mark.it("should fail to add a custom model when there already is a default model with the same name")
def test_add_custom_model_with_same_name_as_default_model(test_client):
    test_client, token = test_client
    response = test_client.post(
        "/models",
        json={"name": DEFAULT_MODEL["public_name"], "nationalities": ["japanese", "dutch"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_EXISTS"


@pytest.mark.order(6)
@pytest.mark.it("should add a new user-to-model entry when creating a custom model with the same classes of another users model")
def test_add_custom_model_with_existing_classes_other_user(test_client):
    test_client, token = test_client

    new_model_name = "custom-model-4"

    response = test_client.post(
        "/models",
        json={"name": new_model_name, "nationalities": EXISTING_CUSTOM_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    test_user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    model_id = generate_model_id(EXISTING_CUSTOM_MODEL["nationalities"])
    expected_response_data = {"message": "Model added successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id, model_id=model_id, name=new_model_name).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.order(7)
@pytest.mark.it("should add a new model and user-to-model entry when creating a model which has the same model name of another user")
def test_add_custom_model_with_existing_name_other_user(test_client):
    test_client, token = test_client
    response = test_client.post(
        "/models",
        json={"name": EXISTING_CUSTOM_MODEL["name"], "nationalities": ["greek", "french"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    test_user_id = User.query.filter_by(email=TEST_USER["email"]).first().id
    model_id = generate_model_id(["greek", "french"])
    expected_response_data = {"message": "Model added successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert UserToModel.query.filter_by(user_id=test_user_id, model_id=model_id, name=EXISTING_CUSTOM_MODEL["name"]).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.order(8)
@pytest.mark.it("should fail to add a new model when token is invalid")
def test_add_custom_model_with_invalid_token(test_client):
    test_client, token = test_client

    token = str(hashlib.sha256("random-long-sequence".encode("utf-8")))
    response = test_client.post(
        "/models",
        json={"name": CUSTOM_MODEL["name"], "nationalities": CUSTOM_MODEL["nationalities"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.order(9)
@pytest.mark.it("should retrieve all custom and default models when the user is authenticated")
def test_get_all_models(test_client):
    test_client, token = test_client
    response = test_client.get("/models", headers={"Authorization": f"Bearer {token}"})
    response_data = json.loads(response.data)
    GetModelsResponseSchema(**response_data["data"])

    assert len(response_data["data"]["customModels"]) == 5
    assert len(response_data["data"]["defaultModels"]) == 1


@pytest.mark.order(10)
@pytest.mark.it("should fail to retrieve all custom and default models when token is invalid")
def test_get_all_models_with_invalid_token(test_client):
    test_client, token = test_client

    token = str(hashlib.sha256("random-long-sequence".encode("utf-8")))
    response = test_client.get("/models",headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


@pytest.mark.order(11)
@pytest.mark.it("should retrieve all default models when user is not authenticated")
def test_get_default_models(test_client):    
    test_client, _ = test_client
    response = test_client.get("/default-models")
    response_data = json.loads(response.data)
    [N2EModel(**model) for model in response_data["data"]]


@pytest.mark.order(12)
@pytest.mark.it("should fail to delete model when token is invalid")
def test_delete_model_with_invalid_token(test_client):
    test_client, token = test_client

    token = str(hashlib.sha256("random-long-sequence".encode("utf-8")))
    response = test_client.delete(
        "/models",
        json={"names": [CUSTOM_MODEL["name"]]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.order(13)
@pytest.mark.it("should remove user-to-model entry but keep the model itself when user deletes custom model")
def test_delete_model(test_client):
    test_client, token = test_client
    response = test_client.delete(
        "/models",
        json={"names": [CUSTOM_MODEL["name"]]},
        headers={"Authorization": f"Bearer {token}"}
    )
    model_id = generate_model_id(CUSTOM_MODEL["nationalities"])
    expected_response_data = {"message": "Model(-s) deleted successfully."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert Model.query.filter_by(id=model_id).first() is not None

