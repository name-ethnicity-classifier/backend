
from errors import CustomError, InferenceError
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
import traceback
from sqlalchemy.exc import SQLAlchemyError 
from utils import success_response, error_response, check_user_existence
from schemas.inference_schema import InferenceSchema
from inference import inference
from services.model_services import get_model_id_by_name

inference_routes = Blueprint("inference", __name__)


@inference_routes.route("/classify", methods=["POST"])
@jwt_required()
def classification_route():
    """ Route for classiying names into ethnicities """

    current_app.logger.info(f"Received classification request.")

    try:
        # Retrieve user id by decoding JWT token
        user_id = get_jwt_identity()

        request_data = InferenceSchema(**request.json)

        # Get model id by name
        model_id = get_model_id_by_name(user_id, request_data.modelName)

        # Classify names
        prediction = inference.predict(
            model_id=model_id,
            names=request_data.names,
            get_distribution=request_data.getDistribution
        )

        response_data = dict(zip(request_data.names, prediction))

        current_app.logger.info("Successfully classified names.")
        return success_response(data=response_data)
    
    # Handle Pydantic schema validation errors
    except ValidationError as e:
        current_app.logger.error("Model data validation failed. Error:\n{e}")
        return error_response(
            error_code="INVALID_MODEL_DATA", message="Invalid model data.", status_code=422
        )
    
    # Handle inference errors
    except InferenceError as e:
        current_app.logger.error(f"Classification failed. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=300
        )
    
    # Handle custom errors
    except CustomError as e:
        current_app.logger.error(f"Classification failed. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code=e.error_code, message=e.message, status_code=e.status_code
        )
    
    # Handle SQLAlchemy errors
    except SQLAlchemyError as e:
        current_app.logger.error(f"Failed query model name. Error:\n{e}")
        return error_response(
            error_code="SERVER_SIDE_ERROR", message="Failed query model name.", status_code=500
        )
    
    # Handle unexpected errors
    except Exception as e:
        current_app.logger.error(f"Unexpected error while classifying names. Error:\n{e}. Traceback:\n{traceback.format_exc()}")
        return error_response(
            error_code="UNEXPECTED_ERROR", message="Unexpected error.", status_code=500
        )
