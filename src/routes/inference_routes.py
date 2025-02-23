from errors import error_handler
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_spec_gen import openapi_generator as og
from services.user_services import check_user_existence
from utils import success_response
from schemas.inference_schema import InferenceSchema, InferenceResponseSchema, InferenceDistributionResponseSchema
from inference import inference
from services.model_services import get_model_id_by_name
from services.inference_services import increment_request_counter


inference_routes = Blueprint("inference", __name__)


@inference_routes.route("/classify", methods=["POST"])
@og.register_route(
    description="Classify names.",
    tags=["Classification"],
    requests=[og.OAIRequest("Request body for classification", InferenceSchema)],
    responses=[
        og.OAIResponse(200, "Successful classification", InferenceResponseSchema),
        og.OAIResponse(401, "Authentication failed"),
        og.OAIResponse(404, "Model not found"),
        og.OAIResponse(422, "Too many names"),
        og.OAIResponse(500, "Internal server error"),
    ]
)
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
        get_distribution=False
    )

    response_data = dict(zip(request_data.names, prediction))
    InferenceResponseSchema(**response_data)

    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)
  

@inference_routes.route("/classify-distribution", methods=["POST"])
@og.register_route(
    description="Classify names (entire distribution).",
    tags=["Classification"],
    requests=[og.OAIRequest("Request body for classification", InferenceSchema)],
    responses=[
        og.OAIResponse(200, "Successful classification", InferenceResponseSchema),
        og.OAIResponse(401, "Authentication failed"),
        og.OAIResponse(404, "Model not found"),
        og.OAIResponse(422, "Too many names"),
        og.OAIResponse(500, "Internal server error"),
    ]
)
@jwt_required()
@error_handler
def classification_distribution_route():
    """ Route for classiying names into an ethnicity condfidence distribution """

    current_app.logger.info(f"Received distribution classification request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = InferenceSchema(**request.json)
    model_id = get_model_id_by_name(user_id, request_data.modelName)

    prediction = inference.predict(
        model_id=model_id,
        names=request_data.names,
        get_distribution=True
    )

    response_data = dict(zip(request_data.names, prediction))
    InferenceDistributionResponseSchema(**response_data)
 
    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)