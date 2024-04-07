import re
from email_validator import validate_email, EmailNotValidError
from flask import Response, jsonify
import json

from db.tables import User
from errors import CustomError


def error_response(error_code: str, message: str, status_code: int) -> Response:
    """
    Creates a JSON serialized Flask error response
    :param message: Error message
    :param status_code: Error status Code
    :return: Flask response
    """

    response = jsonify({"errorCode": error_code, "message": message})
    response.status_code = status_code
    return response


def success_response(message: str = None, data: dict = None, status_code: int = 200) -> Response:
    """
    Creates a JSON serialized Flask success response
    :param message: Success message
    :param status_code: Success status Code
    :return: Flask response
    """
    
    # Only response message (for GET requests)
    if message and not data:
        response_data = {
            "message": message
        }

    # Only response data
    elif data and not message:
        response_data = data

    # Both, response message and data
    elif data and message:
        response_data = {
            "message": message,
            "data": data
        }

    # Response message and/or body must be set
    else:
        raise ValueError("Provide a success message and/or a response body.")

    response = jsonify(response_data)
    response.status_code = status_code
    return response


def to_snake_case(input_string: str) -> str:
    """
    Converts CamelCase strings into snake_case (created by ChatGPT)
    :param input_string: String to convert
    :return: String converted to snake case
    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in input_string]).lstrip("_")


def to_camel_case(input_string: str) -> str:
    """
    Converts snake_case strings into CamelCase (created by ChatGPT)
    :param input_string: String to convert
    :return: String converted to CamelCase
    """
    words = input_string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def is_strong_password(password: str) -> bool:
    """
    Checks if a password is strong enough, ie.
    it has at least 8 characters, at least one lower and one upper case and at least one number.
    :param password: The password to check
    :return: If it is strong enough or not
    """
    
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')
    return bool(pattern.match(password))


def is_valid_email(email: str) -> bool:
    """
    Checks if a string is a valid email.
    :param email: The email to check
    :return: If it is valid or not
    """
    
    try:
        _ = validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        return False


def get_nationalities() -> dict:
    """
    Reads all available nationalities and groups along with their amount of names.
    :return: Dictionary with all nationalities
    """

    return load_json("./data/nationalities.json")


def check_requested_nationalities(requested_nationalities: list[str]) -> int:
    """
    Checks weather a requested nationality configuration is valid, ie. all nationalities do exist
    and are either all normal nationalities or all nationality groups (eg. eastAsian, arabic, etc.).
    :param requested_nationalities: Request nationality configuration
    :return: 0 if valid normal nationalities, 1 if valid nationality groups, -1 if invalid
    """
    
    nationalities = get_nationalities()["nationalities"].keys()
    nationality_groups = get_nationalities()["nationalityGroups"].keys()

    if set(requested_nationalities).issubset(list(nationalities) + ["else"]):
        return 0
    elif set(requested_nationalities).issubset(list(nationality_groups) + ["else"]):
        return 1
    return -1


def check_user_existence(user_id) -> None:
    """
    Checks if user with given ID exists in the database, to make sure
    that even when a user is deleted their JWT token doesn't work anymore.
    :param user_id: User id to check
    """
    
    user = User.query.filter_by(id=user_id).first()

    if not user:
        raise CustomError(
            error_code="AUTHENTICATION_FAILED",
            message="User does not exist.",
            status_code=401
        )


def load_json(file_path: str) -> dict:
    """
    Loads content from a JSON file.
    :param file_path: Path the the JSON file
    :return: JSON content as a dictionary
    """

    with open(file_path, "r") as f:
        return json.load(f)