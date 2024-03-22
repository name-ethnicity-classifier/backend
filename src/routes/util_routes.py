from utils import get_nationalities
from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
import traceback
from sqlalchemy.exc import SQLAlchemyError 
from utils import success_response, error_response, get_nationalities, check_user_existence


util_routes = Blueprint("utils", __name__)


@util_routes.route("/nationalities", methods=["GET"])
@jwt_required()
def get_nationalities_route():
    """ Route for model requests """

    current_app.logger.info(f"Received nationality data request.")

    # Add model to database
    try:
        # Retrieve user id by decoding JWT token
        user_id = get_jwt_identity()

        # Check if user exists
        check_user_existence(user_id)
    
        # Load nationality data
        nationalities = get_nationalities()

        current_app.logger.info("Successfully loaded nationalities.")
        return success_response(response_body=nationalities)

    # Handle unexpected errors
    except Exception as e:
        current_app.logger.error(f"Unexpected error while loading nationality data. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )
