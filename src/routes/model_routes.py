from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
import traceback
from sqlalchemy.exc import SQLAlchemyError 
from schemas.model_schema import AddModelSchema, DeleteModelSchema
from services.model_services import add_model, get_models, delete_models
from utils import success_response, error_response, check_user_existence
from errors import CustomError

model_routes = Blueprint("models", __name__)


@model_routes.route("/models", methods=["POST"])
@jwt_required()
def add_model_route():
    """ Route for model requests """

    current_app.logger.info(f"Received model request.")

    # Add model to database
    try:
        # Retrieve user id by decoding JWT token
        user_id = get_jwt_identity()

        # Check if user exists
        check_user_existence(user_id)
    
        # Validate request body
        request_data = AddModelSchema(**request.json)

        add_model(user_id, request_data)
        current_app.logger.info("Successfully added model data to database.")
        return success_response(message="Model added successfully.")

    # Handle Pydantic schema validation errors
    except ValidationError as e:
        current_app.logger.error("Model data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_MODEL_DATA", message="Invalid model data.", status_code=422
        )

    # Handle custom thrown errors
    except CustomError as e:
        current_app.logger.error(f"Failed to process model data. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )

    # Handle SQLAlchemy errors
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to store model data. Error:\n{e}")
        return error_response(
            error_code="SERVER_SIDE_ERROR", message="Failed to store model data.", status_code=500
        )

    # Handle unexpected errors
    except Exception as e:
        current_app.logger.error(f"Unexpected error while processing model data. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )


@model_routes.route("/models", methods=["DELETE"])
@jwt_required()
def delete_models_route():
    """ Route for deleting models """

    current_app.logger.info(f"Received model deletion request.")

    # Delete model data from database
    try:
        # Retrieve user id by decoding JWT token
        user_id = get_jwt_identity()

        # Check if user exists
        check_user_existence(user_id)

        # Validate request body
        request_data = DeleteModelSchema(**request.json)
    
        delete_models(user_id, request_data)
        current_app.logger.info(f"Successfully deleted model(-s) from user with user id {user_id}.")
        return success_response(message="Model(-s) deleted successfully.")

    # Handle Pydantic schema validation errors
    except ValidationError as e:
        current_app.logger.error("Model data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_MODEL_DATA", message="Invalid model data.", status_code=422
        )

    # Handle custom thrown errors
    except CustomError as e:
        current_app.logger.error(f"Failed to delete model. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )

    # Handle SQLAlchemy errors
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to delete model. Error:\n{e}")
        return error_response(
            error_code="SERVER_SIDE_ERROR", message="Failed to delete model.", status_code=500
        )

    # Handle unexpected errors
    except Exception as e:
        current_app.logger.error(f"Unexpected error. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )


@model_routes.route("/models", methods=["GET"])
@jwt_required()
def get_models_route():
    """ Route for requesting model data """

    current_app.logger.info(f"Received model retrieval request.")

    # Get model data from database
    try:
        # Retrieve user id by decoding JWT token
        user_id = get_jwt_identity()

        # Check if user exists
        check_user_existence(user_id)
    
        model_data = get_models(user_id)
        current_app.logger.info(f"Successfully received model data from user with user id {user_id}.")
        return success_response(
            message="Model data received successfully.",
            data=model_data
        )

    # Handle custom thrown errors
    except CustomError as e:
        current_app.logger.error(f"Failed to receive model data. Error:\n{e.message}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )

    # Handle SQLAlchemy errors
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed to receive model data. Error:\n{e}")
        return error_response(
            error_code="SERVER_SIDE_ERROR", message="Failed to store model data.", status_code=500)

    # Handle unexpected errors
    except Exception as e:
        current_app.logger.error(f"Unexpected error. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )
