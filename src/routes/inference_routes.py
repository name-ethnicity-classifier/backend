
from errors import error_handler
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
import traceback
from sqlalchemy.exc import SQLAlchemyError 
from services.user_services import check_user_existence
from utils import success_response, error_response
from schemas.inference_schema import InferenceSchema
from inference import inference
from services.model_services import get_model_id_by_name
from services.inference_services import increment_request_counter

inference_routes = Blueprint("inference", __name__)


@inference_routes.route("/classify", methods=["POST"])
@jwt_required()
@error_handler
def classification_route():
    """ Route for classiying names into ethnicities """

    current_app.logger.info(f"Received classification request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = InferenceSchema(**request.json)
    model_id = get_model_id_by_name(user_id, request_data.modelName)

    prediction = inference.predict(
        model_id=model_id,
        names=request_data.names,
        get_distribution=request_data.getDistribution
    )
    response_data = dict(zip(request_data.names, prediction))

    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)
  