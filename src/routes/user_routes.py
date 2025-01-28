from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token

from schemas.user_schema import LoginSchema, SignupSchema, DeleteUser
from services.user_services import add_user, check_user_login, delete_user, handle_email_verification, check_user_existence
from utils import success_response
from errors import error_handler

user_routes = Blueprint("user", __name__)


@user_routes.route("/signup", methods=["POST"])
@error_handler
def register_user_route():
    """ Route for signing up the user """

    current_app.logger.info(f"Received signup request.")

    request_data = SignupSchema(**request.json)

    # Validates name, email and password and adds user
    add_user(request_data)

    # Send verification email
    # send_verification_email(request_data.email)

    return success_response("Registration successful.")


@user_routes.route("/login", methods=["POST"])
@error_handler
def login_user_route():
    """ Route for logging in the user """

    current_app.logger.info(f"Received login request.")

    request_data = LoginSchema(**request.json)
    user_id = check_user_login(request_data)

    return success_response(data={
        "accessToken": create_access_token(identity=user_id)
    })


@user_routes.route("/delete-user", methods=["DELETE"])
@jwt_required()
@error_handler
def delete_user_route():
    """ Route for deleting a user """

    current_app.logger.info(f"Received user deletion request.")

    # Retrieve user id by decoding JWT token and check if the user still exists
    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = DeleteUser(**request.json)
    delete_user(user_id, request_data)

    return success_response("User deletion successful.")


@user_routes.route("/verify/<token>", methods=["GET"])
def verify_email(token: str):
    handle_email_verification(token)