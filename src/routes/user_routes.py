from flask import Blueprint, redirect, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token

from schemas.user_schema import LoginSchema, SignupSchema, DeleteUser
from services.user_services import add_user, check_user_login, delete_user, handle_email_verification, check_user_existence, send_verification_email
from utils import error_response, success_response
from errors import error_handler

user_routes = Blueprint("user", __name__)


@user_routes.route("/signup", methods=["POST"])
@error_handler
def register_user_route():
    """ Route for signing up the user """

    current_app.logger.info(f"Received signup request.")

    request_data = SignupSchema(**request.json)
    add_user(request_data)

    return success_response("Registration successful.")


@user_routes.route("/login", methods=["POST"])
@error_handler
def login_user_route():
    """ Route for logging in the user """

    current_app.logger.info(f"Received login request.")

    request_data = LoginSchema(**request.json)
    user = check_user_login(request_data)

    if not user.verified:
        current_app.logger.info(f"User not verified, resending confirmation email.")
        send_verification_email(user.email)
        return error_response("VERIFICATION_ERROR", "User not verified.", 401)

    return success_response(
        data={"accessToken": create_access_token(identity=user.id)}
    )


@user_routes.route("/delete-user", methods=["DELETE"])
@jwt_required()
@error_handler
def delete_user_route():
    """ Route for deleting a user """

    current_app.logger.info(f"Received user deletion request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = DeleteUser(**request.json)
    delete_user(user_id, request_data)

    return success_response("User deletion successful.")


@user_routes.route("/verify/<token>", methods=["GET"])
def verify_email(token: str):
    """ Route verifying a user """

    handle_email_verification(token)

    return redirect(f"{current_app.config['FRONTEND_URL']}/login", code=302)