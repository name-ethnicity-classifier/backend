from flask import Blueprint, request, current_app
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError 
from flask_limiter import RateLimitExceeded
from flask_jwt_extended import create_access_token

from schemas.user_schema import LoginSchema, SignupSchema
from services.user_services import add_user, check_user_login
from utils import success_response, error_response
from errors import LoginError, SignupError

authentication_routes = Blueprint("authentication", __name__)


@authentication_routes.route("/signup", methods=["POST"])
def register_user_route():
    """ Route for signing up the user """

    current_app.logger.info(f"Received signup request.")

    try:
        request_data = SignupSchema(**request.json)

        # Validates name, email and password and adds user
        add_user(request_data)

        return success_response("Registration successful.")

    except ValidationError as e:
        current_app.logger.error(f"Signup data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_SIGNUP_DATA", message="Invalid signup data.", status_code=400
        )

    except SignupError as e:
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


@authentication_routes.route("/login", methods=["POST"])
def login_user_route():
    """ Route for logging in the user """

    current_app.logger.info(f"Received login request.")

    try:
        request_data = LoginSchema(**request.json)

        # Check if email and password are correct
        user_id = check_user_login(request_data)

        response_body = {
            "accessToken": create_access_token(identity=user_id)
        }

        return success_response("Authentication successful.", response_body)

    except ValidationError as e:
        current_app.logger.error(f"Login data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_LOGIN_DATA", message="Invalid login data.", status_code=400
        )

    except LoginError as e:
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
