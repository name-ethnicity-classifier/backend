import re
from email_validator import validate_email, EmailNotValidError
from flask import Response, jsonify
import json


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


def success_response(message: str, response_body: dict = None, status_code: int = 200) -> Response:
    """
    Creates a JSON serialized Flask success response
    :param message: Success message
    :param status_code: Success status Code
    :return: Flask response
    """
    
    response_data = {"message": message}
    if response_body:
        response_data["data"] = response_body

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

    with open("./data/nationalities.json", "r") as f:
        return json.load(f)


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


