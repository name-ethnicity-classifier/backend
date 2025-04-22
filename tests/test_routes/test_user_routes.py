import pytest
import json
from unittest.mock import patch
from sqlalchemy import text
from utils import *
from app import app
from db.database import db
from db.tables import AccessLevel, User


TEST_USER_REQUEST_BODY = {
    "name": "user",
    "email": "teddypeifer@gmail.com",
    "role": "else",
    "password": "StrongPassword123",
    "consented": True,
    "usageDescription": "Lorem Ipsum" * 10,     # use camelCase bc this is the entity for the API request body
    "verified": True,
}
TEST_USER_ID = 1


@pytest.fixture(scope="function")
def app_context():
    with app.app_context():

        app.config["USER_VERIFICATION_ACTIVE"] = False

        db.drop_all()
        with open("./dev-infrastructure/db-seed/init.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))
        db.session.commit()

        yield app


@pytest.fixture(scope="function")
def test_client(app_context):
    return app_context.test_client()


@pytest.fixture(scope="function", autouse=True)
def mock_resend_email_send(request):
    with patch("resend.Emails.send") as mock_send:
        mock_send.return_value = {"id": 123}
        request.node.mock_resend_email_send = mock_send

        yield mock_send


@pytest.mark.it("should fail to signup user when signup data is invalid")
def test_signup_user_with_invalid_data(test_client):
    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["name"] = "a"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "INVALID_NAME"

    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["email"] = "invalidemail"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "INVALID_EMAIL"

    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["password"] = "weakpassword"
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "PASSWORD_TOO_WEAK"

    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["password"] = "a" * 1000
    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "PASSWORD_TOO_LONG"


@pytest.mark.it("should fail to signup user when signup schema is invalid")
def test_signup_user_with_invalid_schema(test_client):
    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["E-Mail"] = TEST_USER_REQUEST_BODY["email"]
    del signup_data["email"]

    response = test_client.post("/signup", json=signup_data)
    assert response.status_code == 400
    assert json.loads(response.data)["errorCode"] == "VALIDATION_ERROR"


@pytest.mark.it("should fail to signup user when they don't consent to ToS")
def test_signup_user_given_no_consent(test_client):
    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["consented"] = False
    response = test_client.post("/signup", json=signup_data)

    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "NO_CONSENT"


@pytest.mark.it("should fail to signup user when they don't provide a valid usage description")
def test_signup_user_with_invalid_usage_description(test_client):
    signup_data = TEST_USER_REQUEST_BODY.copy()
    signup_data["usageDescription"] = "Too short."
    response = test_client.post("/signup", json=signup_data)

    assert response.status_code == 422
    assert json.loads(response.data)["errorCode"] == "INVALID_USAGE_DESCRIPTION"


@pytest.mark.it("should create to user entry and send verification email when user signs up successfully")
def test_signup_user(test_client, request):
    app.config["USER_VERIFICATION_ACTIVE"] = True   # in case this was deactived during developing

    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)

    assert response.status_code == 200

    user = User.query.filter_by(email=TEST_USER_REQUEST_BODY["email"]).first()
    assert user is not None
    assert user.access.lower() == AccessLevel.PENDING.value
    request.node.mock_resend_email_send.assert_called_once()    # check if email would be sent


@pytest.mark.it("should fail to signup user when other user already has same email address")
def test_signup_user_with_existing_email(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200
    
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "EMAIL_EXISTS"


@pytest.mark.it("should fail to signup user when other user already has same email address but with different casing")
def test_signup_user_with_existing_email_uppercase(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    same_user = TEST_USER_REQUEST_BODY.copy()
    same_user["email"] = same_user["email"].upper()
    
    response = test_client.post("/signup", json=same_user)
    assert response.status_code == 409
    assert json.loads(response.data)["errorCode"] == "EMAIL_EXISTS"


@pytest.mark.it("should fail to login and resend email when user is not verified")
def test_login_user_not_verified(test_client, request):
    app.config["USER_VERIFICATION_ACTIVE"] = True

    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "VERIFICATION_ERROR"
    request.node.mock_resend_email_send.assert_called()


@pytest.mark.it("should return JWT token when user logs in successully")
def test_login_user(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 200
    assert "accessToken" in json.loads(response.data)


@pytest.mark.it("should return JWT token when user logs in successully but with different email casing")
def test_login_user_email_uppercase(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"].upper(), "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 200
    assert "accessToken" in json.loads(response.data)


@pytest.mark.it("should fail to login user when email does not exist")
def test_login_not_existing_user(test_client):
    response = test_client.post(
        "/login",
        json={"email": "doesnt@exist.com", "password": "password"}
    )
    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "AUTHENTICATION_FAILED"


@pytest.mark.it("should fail to login user when login schema is invalid")
def test_login_invalid_user_schema(test_client):
    login_data = {
        "E-Mail": TEST_USER_REQUEST_BODY["email"],
        "password": TEST_USER_REQUEST_BODY["password"]
    }

    response = test_client.post("/login", json=login_data)
    assert response.status_code == 400
    assert json.loads(response.data)["errorCode"] == "VALIDATION_ERROR"


@pytest.mark.it("should fail to login user when password is wrong")
def test_login_with_wrong_password(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200 
    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": "wrongpassword"}
    )        
    assert response.status_code == 401        
    assert json.loads(response.data)["errorCode"] == "AUTHENTICATION_FAILED"


@pytest.mark.it("should update the usage description successfully")
def test_update_usage_description(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 200
    token = json.loads(response.data)["accessToken"]

    new_usage_description = "This is a new and valid usage description that is long enough."
    response = test_client.put(
        "/update-usage-description",
        json={"usageDescription": new_usage_description},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Usage description updated successfully."}

    updated_user = User.query.filter_by(email=TEST_USER_REQUEST_BODY["email"]).first()
    assert updated_user.usage_description == new_usage_description


@pytest.mark.it("should fail to remove user when trying to delete their account with invalid password")
def test_delete_user_with_wrong_password(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 200
    
    token = json.loads(response.data)["accessToken"]
    response = test_client.delete(
        "/delete-user",
        json={"password": "invalidpassword"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert json.loads(response.data)["errorCode"] == "USER_DELETION_FAILED"
    assert User.query.filter_by(email=TEST_USER_REQUEST_BODY["email"]).first() is not None


@pytest.mark.it("should fail to remove user when trying to delete their account with invalid token")
def test_delete_user_with_invalid_token(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    invalid_token = str(hashlib.sha256("random-long-sequence".encode("utf-8")))
    response = test_client.delete(
        "/delete-user",
        json={"password": TEST_USER_REQUEST_BODY["password"]},
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 422
    assert User.query.filter_by(email=TEST_USER_REQUEST_BODY["email"]).first() is not None


@pytest.mark.it("should remove user entry when user deletes their account")
def test_delete_user(test_client):
    response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert response.status_code == 200

    response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert response.status_code == 200
    
    token = json.loads(response.data)["accessToken"]
    response = test_client.delete(
        "/delete-user",
        json={"password": TEST_USER_REQUEST_BODY["password"]},
        headers={"Authorization": f"Bearer {token}"}
    )

    expected_response_data = {"message": "User deletion successful."}

    assert response.status_code == 200
    assert json.loads(response.data) == expected_response_data
    assert User.query.filter_by(email=TEST_USER_REQUEST_BODY["email"]).first() is None


@pytest.mark.it("should return user access level and the reason for it when user is logged in")
def test_check_user_access_level(test_client):
    signup_response = test_client.post("/signup", json=TEST_USER_REQUEST_BODY)
    assert signup_response.status_code == 200

    login_response = test_client.post(
        "/login",
        json={"email": TEST_USER_REQUEST_BODY["email"], "password": TEST_USER_REQUEST_BODY["password"]}
    )
    assert login_response.status_code == 200
    
    token = json.loads(login_response.data)["accessToken"]
    response = test_client.get(
        "/check",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert json.loads(response.data)["accessLevel"] in [a.value for a in AccessLevel]
    assert json.loads(response.data)["accessLevelReason"] == "pending"