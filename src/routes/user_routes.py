from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError 
from flask_jwt_extended import create_access_token

from schemas.user_schema import LoginSchema, SignupSchema, DeleteUser
from services.user_services import add_user, check_user_login, delete_user, send_verification_email, handle_email_verification
from utils import check_user_existence, success_response, error_response
from errors import CustomError

user_routes = Blueprint("user", __name__)


@user_routes.route("/signup", methods=["POST"])
def register_user_route():
    """ Route for signing up the user """

    current_app.logger.info(f"Received signup request.")

    try:
        request_data = SignupSchema(**request.json)

        # Validates name, email and password and adds user
        add_user(request_data)

        # Send verification email
        # send_verification_email(request_data.email)

        return success_response("Registration successful.")

    except ValidationError as e:
        current_app.logger.error(f"Signup data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_SIGNUP_DATA", message="Invalid signup data.", status_code=400
        )

    except CustomError as e:
        current_app.logger.error(f"Failed to sign up user. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )
    
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to query user data. Error:\n{e}")
        return error_response(
            error_code="AUTHENTICATION_FAILED", message="Couldn't add user.", status_code=500
        )

    except Exception as e:
        current_app.logger.error(f"Unexpected error while signing up user. Error:\n{e}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )


@user_routes.route("/login", methods=["POST"])
def login_user_route():
    """ Route for logging in the user """

    current_app.logger.info(f"Received login request.")

    try:
        request_data = LoginSchema(**request.json)

        # Check if email and password are correct
        user_id = check_user_login(request_data)

        response_data = {
            "accessToken": create_access_token(identity=user_id)
        }

        return success_response("Authentication successful.", response_data)

    except ValidationError as e:
        current_app.logger.error(f"Login data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_LOGIN_DATA", message="Invalid login data.", status_code=400
        )

    except CustomError as e:
        current_app.logger.error(f"Failed to login user. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )
    
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to query user data. Error:\n{e}")
        return error_response(
            error_code="AUTHENTICATION_FAILED", message="Email or password not found.", status_code=500
        )

    except Exception as e:
        current_app.logger.error(f"Unexpected error while logging in user. Error:\n{e}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )


@user_routes.route("/delete-user", methods=["DELETE"])
@jwt_required()
def delete_user_route():
    """ Route for deleting a user """

    current_app.logger.info(f"Received user deletion request.")

    try:
        # Retrieve user id by decoding JWT token and check if the user still exists
        user_id = get_jwt_identity()
        check_user_existence(user_id)

        request_data = DeleteUser(**request.json)

        delete_user(user_id, request_data)

        return success_response("User deletion successful.")

    except ValidationError as e:
        current_app.logger.error(f"User deletion data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_USER_DELETION_DATA", message="Invalid user deletion data.", status_code=400
        )

    except CustomError as e:
        current_app.logger.error(f"Failed to delete user. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )
    
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to query user data. Error:\n{e}")
        return error_response(
            error_code="USER_DELETION_FAILED", message="Email or password not found.", status_code=500
        )

    except Exception as e:
        current_app.logger.error(f"Unexpected error while trying to delete user. Error:\n{e}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )


@user_routes.route("/verify/<token>", methods=["GET"])
def verify_email(token: str):
    handle_email_verification(token)