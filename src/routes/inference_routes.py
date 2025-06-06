from errors import error_handler
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_spec_gen import openapi_generator as og
from services.user_services import check_user_existence, check_user_restriction
from utils import success_response
from schemas.inference_schema import InferenceSchema, InferenceResponseSchema, InferenceDistributionResponseSchema
from inference import inference
from services.model_services import get_inference_model_info
from services.inference_services import check_name_amount_and_quota, increment_request_counter, update_name_quota


inference_routes = Blueprint("inference", __name__)


@inference_routes.route("/classify", methods=["POST"])
@og.register_route(
    summary="Classify names.",
    description="Classifying names using this endpoint will return the predicted confidence for the most likely ethnicity.",
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
    check_user_restriction(user_id)

    request_data = InferenceSchema(**request.json)
    model_id, classes = get_inference_model_info(user_id, request_data.modelName)
    check_name_amount_and_quota(user_id, len(request_data.names))

    prediction = inference.predict(
        model_id=model_id,
        classes=classes,
        names=request_data.names,
        batch_size=int(current_app.config["BATCH_SIZE"]),
        get_distribution=False
    )

    response_data = dict(zip(request_data.names, prediction))
    InferenceResponseSchema(**response_data)

    update_name_quota(user_id, len(request_data.names))
    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)
  

@inference_routes.route("/classify-distribution", methods=["POST"])
@og.register_route(
    summary="Classify names, predicting entire distribution.",
    description="Classifying names using this endpoint will return the predicted confidence for each ethnicity.",
    tags=["Classification"],
    requests=[og.OAIRequest("Request body for classification", InferenceSchema)],
    responses=[
        og.OAIResponse(200, "Successful classification", InferenceDistributionResponseSchema),
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
    check_user_restriction(user_id)

    request_data = InferenceSchema(**request.json)
    model_id, classes = get_inference_model_info(user_id, request_data.modelName)
    check_name_amount_and_quota(user_id, len(request_data.names))

    prediction = inference.predict(
        model_id=model_id,
        classes=classes,
        names=request_data.names,
        batch_size=int(current_app.config["BATCH_SIZE"]),
        get_distribution=True
    )

    response_data = dict(zip(request_data.names, prediction))
    InferenceDistributionResponseSchema(**response_data)
 
    update_name_quota(user_id, len(request_data.names))
    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)