from flask import jsonify
import pytest
import json
from utils import *
from app import app


@pytest.fixture
def app_context():
    # Create Flask application context for testing
    with app.app_context():
        app.config.update({
            "TESTING": True,
        })
        yield app


def test_error_response(app_context):
    # Test error response
    response = error_response(
        error_code="TEST_ERROR",
        message="Test error message.",
        status_code=404
    )

    assert json.loads(response.data) == {"errorCode": "TEST_ERROR", "message": "Test error message."}
    assert response.status_code == 404


def test_success_response(app_context):
    # Test success response with default status code
    response = success_response(
        message="Test success message.",
    )

    assert json.loads(response.data) == {"message": "Test success message."}
    assert response.status_code == 200

    # Test success response with specific status code
    response = success_response(
        message="Test success message.",
        status_code=205
    )

    assert json.loads(response.data) == {"message": "Test success message."}
    assert response.status_code == 205


def test_to_snake_case():
    camel_case_str = "aTestString"
    assert to_snake_case(camel_case_str) == "a_test_string"

    camel_case_str = "ATestString"
    assert to_snake_case(camel_case_str) == "a_test_string"

    camel_case_str = "AnotherTestString"
    assert to_snake_case(camel_case_str) == "another_test_string"

    camel_case_str = "string"
    assert to_snake_case(camel_case_str) == "string"

    camel_case_str = "String"
    assert to_snake_case(camel_case_str) == "string"


def test_to_camel_case():
    snake_case_str = "a_test_string"
    assert to_camel_case(snake_case_str) == "aTestString"

    snake_case_str = "another_test_string"
    assert to_camel_case(snake_case_str) == "anotherTestString"

    snake_case_str = "string"
    assert to_camel_case(snake_case_str) == "string"

    snake_case_str = "snake_case_string"
    assert to_camel_case(snake_case_str) == "snakeCaseString"

    snake_case_str = "camelCaseString"
    assert to_camel_case(snake_case_str) == "camelCaseString"


def test_is_strong_password():
    assert is_strong_password("StrongPass123") == True
    assert is_strong_password("WeakPwd") == False
    assert is_strong_password("NoDigitHere") == False
    assert is_strong_password("") == False


def test_is_valid_email():
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("invalid.email") == False
    assert is_valid_email("@missingusername.com") == False
    assert is_valid_email("test@missingdomain.") == False


def test_check_requested_nationalities():
    requested_nationalities = ["chinese", "else"]
    assert check_requested_nationalities(requested_nationalities) == 0
    
    requested_nationalities = ["eastAsian", "arabic"]
    assert check_requested_nationalities(requested_nationalities) == 1

    requested_nationalities = ["neverlander", "greek"]
    assert check_requested_nationalities(requested_nationalities) == -1

    requested_nationalities = ["scandinavian", "czech"]
    assert check_requested_nationalities(requested_nationalities) == -1

