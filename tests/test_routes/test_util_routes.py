from unittest.mock import patch
from flask import jsonify
from flask_jwt_extended import create_access_token
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
    "consented": True,
    "verified": True,
    "usage_description": "Lorem Ipsum" * 10
}
TEST_USER_ID = 1


@pytest.fixture(scope="function")
def app_context():
    with app.app_context():
        db.drop_all()
        with open("./dev-database/init_test.sql", "r") as file:
            init_sql_script = file.read()    
            db.session.execute(text(init_sql_script))

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
    user_id = 2
    with patch("flask_jwt_extended.get_jwt_identity") as mock_identity:
        mock_identity.return_value = user_id

        with app.test_request_context():
            token = create_access_token(identity=user_id)
        test_client.token = token
        yield test_client


@pytest.mark.it("should retrieve a nationalities and nationality groups when not authenticated")
def test_get_nationalities(test_client):
    response = test_client.get("/nationalities")
                              
    assert response.status_code == 200
    assert json.loads(response.data) == get_nationalities()