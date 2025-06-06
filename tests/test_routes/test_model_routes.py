import os
from unittest.mock import patch
from flask_jwt_extended import create_access_token
import pytest
import json
from schemas.model_schema import ModelsResponseSchema
from utils import *
from app import app
from db.database import db
from db.tables import User, Model, UserToModel, AccessLevel
from sqlalchemy import text


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

EXISTING_USER = {
    "name": "existing-test-user",
    "email": "existing.user@test.com",
    "role": "student",
    "password": "Hashedpassword123",
    "consented": True,
    "usage_description": "Lorem Ipsum" * 10,
    "access": AccessLevel.FULL.value,
    "verified": True,
}
EXISTING_USER_ID = 1
EXISTING_CUSTOM_MODEL = {
    "public_name": None,
    "nationalities": (classes := sorted(set(["japanese", "else"]))),
    "accuracy": 98.5,
    "scores": [98.0, 99.0],
    "is_trained": True,
    "is_grouped": False,
    "is_public": False,
    "id": generate_model_id(classes),
}
EXISTING_USER_TO_MODEL = {
    "model_id": EXISTING_CUSTOM_MODEL["id"],
    "user_id": EXISTING_USER_ID,
    "request_count": 0,
    "name": "existing-custom-model",
    "description": "Model for unit testing."
}

TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True,
    "usage_description": "Lorem Ipsum" * 10,
    "access": AccessLevel.FULL.value,
    "verified": True
}
TEST_USER_ID = 2


@pytest.fixture(scope="function")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-infrastructure/db-seed/init.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))

        db.session.add(Model(**DEFAULT_MODEL))
        db.session.add(User(**EXISTING_USER))
        db.session.add(Model(**EXISTING_CUSTOM_MODEL))
        db.session.add(UserToModel(**EXISTING_USER_TO_MODEL))
        db.session.add(User(**TEST_USER))
        db.session.commit()

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
def mock_max_models_env():
    with patch("src.model_services.os.getenv", side_effect=(lambda arg: 0 if arg == "MAX_MODELS" else os.getenv(arg))):
        yield


@pytest.fixture
def mock_bcrypt_checkpw():
    with patch("bcrypt.checkpw", return_value=True):
        yield


@pytest.mark.it("should add a new model and user-to-model entry when user creates custom model")
def test_add_custom_model(authenticated_client):
    model_name = "new_model"
    classes = ["german", "else"]
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes, "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    model_id = generate_model_id(sorted(set(classes)))
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should add a new model when the user already has a model trained on same nationalities")
def test_add_custom_model_with_same_classes(authenticated_client):
    model_name = "new_model"
    classes = ["german", "else"]
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes, "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 200

    second_model_name = "different_name"
    response = authenticated_client.post(
        "/models",
        json={"name": second_model_name, "nationalities": classes, "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    model_id = generate_model_id(sorted(set(classes)))
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=second_model_name).first() is not None
    assert len(UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id).all()) == 2
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should add a custom model when there already is a default model trained on same nationalities")
def test_add_custom_model_with_same_classes_as_default(authenticated_client):
    model_name = "new_model"
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": DEFAULT_MODEL["nationalities"], "description": None},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    model_id = generate_model_id(DEFAULT_MODEL["nationalities"])
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=model_name).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should fail to add a custom model when the user already has a model with the same name")
def test_add_custom_model_with_same_name(authenticated_client):
    model_name = "new_model"
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": ["japanese", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 200

    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": ["german", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_EXISTS"


@pytest.mark.it("should fail to add a custom model when there already is a default model with the same name")
def test_add_custom_model_with_same_name_as_default_model(authenticated_client):
    response = authenticated_client.post(
        "/models",
        json={"name": DEFAULT_MODEL["public_name"], "nationalities": ["japanese", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_EXISTS"


@pytest.mark.it("should fail to add a custom model when the model name is too long or empty")
def test_add_custom_model_with_invalid_name(authenticated_client):
    too_long_name = "a" * 65
    response = authenticated_client.post(
        "/models",
        json={"name": too_long_name, "nationalities": ["japanese", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_INVALID"

    response = authenticated_client.post(
        "/models",
        json={"name": "", "nationalities": ["japanese", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "MODEL_NAME_INVALID"


@pytest.mark.it("should fail to add a custom model when the model description is too long")
def test_add_custom_model_with_invalid_description(authenticated_client):
    too_long_description = "lorem ipsum" * 301
    response = authenticated_client.post(
        "/models",
        json={"name": "new_model", "nationalities": ["japanese", "else"], "description": too_long_description},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "MODEL_DESCRIPTION_INVALID"


@pytest.mark.it("should fail to add a custom model when the maximum is reached")
def test_add_custom_model_but_maximum_reached(authenticated_client, monkeypatch):
    monkeypatch.setenv("MAX_MODELS", "0")

    response = authenticated_client.post(
        "/models",
        json={"name": "new_model", "nationalities": ["japanese", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 405
    assert json.loads(response.data)["errorCode"] == "MAX_MODELS_REACHED"


@pytest.mark.it("should add a new custom model and user-to-model relation when creating a model with the same name of another users model")
def test_add_custom_model_with_same_name_as_other_users_model(authenticated_client):
    model_name = EXISTING_USER_TO_MODEL["name"]
    classes = ["german", "else"]
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes, "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    model_id = generate_model_id(classes)
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=model_name).first() is not None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should add a new user-to-model entry when creating a custom model with the same classes of another users model")
def test_add_custom_model_with_same_classes_other_user(authenticated_client):
    model_name = "new_model"
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": EXISTING_CUSTOM_MODEL["nationalities"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=EXISTING_CUSTOM_MODEL["id"], name=model_name).first() is not None
    assert Model.query.filter_by(id=EXISTING_CUSTOM_MODEL["id"]).first() is not None


@pytest.mark.it("should add a new user-to-model entry when creating a custom model without a description")
def test_add_custom_model_with_no_description(authenticated_client):
    model_name = "new_model"
    classes = ["german", "else"]
    
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    model_id = generate_model_id(classes)

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Model added successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=model_name).first() is not None
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=model_name).first().description == None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should fail to create new model when access is RESTRICTED")
def test_add_custom_model_with_restricted_access(authenticated_client):
    user = User.query.filter_by(id=TEST_USER_ID).first()
    user.access = AccessLevel.RESTRICTED.value

    model_name = "new_model"
    classes = ["german", "else"]
    
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    
    assert response.status_code == 403
    assert json.loads(response.data)["errorCode"] == "RESTRICTED_ACCESS"


@pytest.mark.it("should retrieve all custom and default models the user has access to")
def test_get_all_models(authenticated_client):
    models_to_create = [
        ("model-1", ["german", "else"]),
        ("model-2", DEFAULT_MODEL["nationalities"]),
        ("model-3", EXISTING_CUSTOM_MODEL["nationalities"]),
    ]

    for name, classes in models_to_create:
        response = authenticated_client.post(
            "/models",
            json={"name": name, "nationalities": classes, "description": ""},
            headers={"Authorization": f"Bearer {authenticated_client.token}"}
        )
    
    response = authenticated_client.get(
        "/models",
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    response_data = json.loads(response.data)

    assert response.status_code == 200
    ModelsResponseSchema(**response_data)
    assert len(response_data["customModels"]) == len(models_to_create)
    assert len(response_data["defaultModels"]) == 1


@pytest.mark.it("should retrieve all default models when user is not authenticated")
def test_get_all_default_models_without_authentication(test_client):
    response = test_client.get("/default-models")
    response_data = json.loads(response.data)

    assert response.status_code == 200
    assert len(response_data) == 1


@pytest.mark.it("should remove user-to-model relation but keep the model itself when user deletes custom model")
def test_delete_custom_model_relation(authenticated_client):
    model_name = "new_model"
    classes = ["german", "else"]
    response = authenticated_client.post(
        "/models",
        json={"name": model_name, "nationalities": classes, "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 200

    response = authenticated_client.delete(
        "/models",
        json={"names": [model_name]},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    model_id = generate_model_id(classes)
    assert json.loads(response.data) == {"message": "Model(-s) deleted successfully."}
    assert UserToModel.query.filter_by(user_id=TEST_USER_ID, model_id=model_id, name=model_name).first() is None
    assert Model.query.filter_by(id=model_id).first() is not None


@pytest.mark.it("should fail when trying to remove a default model")
def test_delete_default_model(authenticated_client):
    response = authenticated_client.delete(
        "/models",
        json={"names": [DEFAULT_MODEL["public_name"]]},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )

    assert response.status_code == 404
    assert json.loads(response.data)["message"] == 'Model does not exist for this user.'
    assert Model.query.filter_by(id=generate_model_id(classes)).first() is not None


@pytest.mark.it("should delete all user-to-model relations when user deletes their account")
def test_delete_default_model(authenticated_client, mock_bcrypt_checkpw):
    response = authenticated_client.post(
        "/models",
        json={"name": "new_model", "nationalities": ["german", "else"], "description": ""},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    assert response.status_code == 200
    assert len(UserToModel.query.filter_by(user_id=TEST_USER_ID).all()) == 1

    response = authenticated_client.delete(
        "/delete-user",
        json={"password": TEST_USER["password"]},
        headers={"Authorization": f"Bearer {authenticated_client.token}"}
    )
    assert response.status_code == 200
    assert len(UserToModel.query.filter_by(user_id=TEST_USER_ID).all()) == 0
