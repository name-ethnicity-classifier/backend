from flask import Blueprint, redirect, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token

from schemas.user_schema import LoginSchema, SignupSchema, DeleteUserSchema, UpdateUsageDescriptionSchema
from services.user_services import add_user, check_user_login, delete_user, handle_email_verification, check_user_existence, send_verification_email, update_usage_description
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


@user_routes.route("/update-usage-description", methods=["PUT"])
@jwt_required()
@error_handler
def update_usage_description_route():
    """ Route for updating the usage description """
    
    current_app.logger.info(f"Received update usage description request.")

    user_id = get_jwt_identity()
    request_data = UpdateUsageDescriptionSchema(**request.json)

    update_usage_description(user_id, request_data.usageDescription)

    return success_response("Usage description updated successfully.")



@user_routes.route("/delete-user", methods=["DELETE"])
@jwt_required()
@error_handler
def delete_user_route():
    """ Route for deleting a user """

    current_app.logger.info(f"Received user deletion request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = DeleteUserSchema(**request.json)
    delete_user(user_id, request_data)

    return success_response("User deletion successful.")


@user_routes.route("/verify/<token>", methods=["GET"])
def verify_email(token: str):
    """ Route verifying a user """

    handle_email_verification(token)

    return redirect(f"{current_app.config['FRONTEND_URL']}/login", code=302)


@user_routes.route("/check", methods=["GET"])
@jwt_required()
@error_handler
def check_user_authorization_and_access():
    """ Route for checking if a user is authenticated and get their access level """
    
    current_app.logger.info(f"Received update usage description request.")

    user_id = get_jwt_identity()
    user = check_user_existence(user_id)
    
    access_level = user.access
    access_level_reason = user.access_level_reason
    
    return success_response(
        data={"accessLevel": access_level, "accessLevelReason": access_level_reason}
    )
