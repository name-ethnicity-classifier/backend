from flask import jsonify
import pytest
import json
from sqlalchemy import text
from utils import *
from app import app
from db.database import db
from db.tables import User


TEST_USER = {
    "name": "user",
    "email": "user@test.com",
    "role": "else",
    "password": "StrongPassword123",
    "verified": True,
    "consented": True
}


@pytest.fixture(scope="session")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))
        db.session.commit()

        yield app


@pytest.fixture(scope="session")
def test_client(app_context):
    return app_context.test_client()


@pytest.mark.order(1)
@pytest.mark.it("should fail to signup user when signup data is invalid")
def test_signup_user_with_invalid_data(test_client):
    signup_data = TEST_USER.copy()
    signup_data["name"] = "a"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "INVALID_NAME"

    signup_data = TEST_USER.copy()
    signup_data["email"] = "invalidemail"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "INVALID_EMAIL"

    signup_data = TEST_USER.copy()
    signup_data["password"] = "weakpassword"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "PASSWORD_TOO_WEAK"

    signup_data = TEST_USER.copy()
    signup_data["password"] = "a" * 1000
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "PASSWORD_TOO_LONG"


@pytest.mark.order(2)
@pytest.mark.it("should fail to signup user when signup schema is invalid")
def test_signup_user_with_invalid_schema(test_client):
    signup_data = TEST_USER.copy()
    signup_data["mail"] = TEST_USER["email"]    # 'mail' instead of 'email'
    del signup_data["email"]

    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 400
    assert json.loads(response.data)["errorCode"] == "INVALID_SIGNUP_DATA"


@pytest.mark.order(3)
@pytest.mark.it("should fail to signup user when they give no consent to ToS")
def test_signup_user_given_no_consent(test_client):
    signup_data = TEST_USER.copy()
    signup_data["consented"] = False
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "NO_CONSENT"


@pytest.mark.order(4)
@pytest.mark.it("should create to user entry when user signs up successfully")
def test_signup_user(test_client):
    response = test_client.post("/signup", json=TEST_USER)
    assert response.status_code == 200
    assert User.query.filter_by(email=TEST_USER["email"]).first() is not None


@pytest.mark.order(5)
@pytest.mark.it("should fail to signup user when other user already has same email address")
def test_signup_user_with_existing_email(test_client):
    response = test_client.post("/signup", json=TEST_USER)
    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "EMAIL_EXISTS"


@pytest.mark.order(6)
@pytest.mark.it("should return JWT token when user logs in successully")
def test_login_user(test_client):
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "accessToken" in json.loads(response.data)["data"]


@pytest.mark.order(7)
@pytest.mark.it("should fail to login user when email does not exist")
def test_login_not_existing_user(test_client):
    login_data = {
        "email": "doesnt@exist.com",
        "password": "password"
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "AUTHENTICATION_FAILED"


@pytest.mark.order(8)
@pytest.mark.it("should fail to login user when login schema is invalid")
def test_login_invalid_user_schema(test_client):
    login_data = {
        "mail": TEST_USER["email"],     # 'mail' instead of 'email'
        "password": TEST_USER["password"]
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 400
    assert json.loads(response.data)["errorCode"] == "INVALID_LOGIN_DATA"


@pytest.mark.order(9)
@pytest.mark.it("should fail to login user when password is wrong")
def test_login_with_wrong_password(test_client):
    login_data = {
        "email": TEST_USER["email"],
        "password": "wrongpassword"
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "AUTHENTICATION_FAILED"


@pytest.mark.order(10)
@pytest.mark.it("should fail to remove user when trying to delete their account with invalid password")
def test_delete_user_with_wrong_password(test_client):
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 200
    
    token = json.loads(response.data)["data"]["accessToken"]
    response = test_client.delete(
        "/delete-user",
        json={"password": "invalidpassword"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "USER_DELETION_FAILED"
    assert User.query.filter_by(email=TEST_USER["email"]).first() is not None


@pytest.mark.order(10)
@pytest.mark.it("should fail to remove user when trying to delete their account with invalid token")
def test_delete_user_with_invalid_token(test_client):
    token = str(hashlib.sha256("random-long-sequence".encode("utf-8")))
    response = test_client.delete(
        "/delete-user",
        json={"password": TEST_USER["password"]},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
    assert User.query.filter_by(email=TEST_USER["email"]).first() is not None


@pytest.mark.order(11)
@pytest.mark.it("should remove user entry when user deletes their account")
def test_delete_user(test_client):
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 200
    
    token = json.loads(response.data)["data"]["accessToken"]
    response = test_client.delete(
        "/delete-user",
        json={"password": TEST_USER["password"]},
        headers={"Authorization": f"Bearer {token}"}
    )

    expected_response_data = {"message": "User deletion successful."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data

    deleted_user = User.query.filter_by(email=TEST_USER["email"]).first()
    assert deleted_user is None