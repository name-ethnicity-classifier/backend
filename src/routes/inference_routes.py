
from errors import error_handler
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from openapi_gen import with_openapi, ResponseSchema, RequestSchema
from services.user_services import check_user_existence
from utils import success_response
from schemas.inference_schema import InferenceSchema, InferenceDistributionResponseSchema, InferenceResponseSchema
from inference import inference
from services.model_services import get_model_id_by_name
from services.inference_services import increment_request_counter
from flask import current_app

inference_routes = Blueprint("inference", __name__)


@inference_routes.route("/classify", methods=["POST"])
@with_openapi(
    description="Route for classifiying names into their most likely ethnicity.",
    tags=["Classification"],
    request_schema=RequestSchema(model=InferenceSchema),
    responses=[
        ResponseSchema(200, "Successful classification", InferenceResponseSchema),
        ResponseSchema(401, "Authentication failed"),
        ResponseSchema(404, "Model not found"),
        ResponseSchema(422, "Too many names"),
        ResponseSchema(500, "Internal server error"),
    ]
)
@jwt_required()
@error_handler
def classification_route():
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


@inference_routes.route("/classify-distribution", methods=["POST"])
@with_openapi(
    description="Route for classifiying names which returns a probability for each possible ethnicity.",
    tags=["Classification"],
    request_schema=RequestSchema(model=InferenceSchema),
    responses=[
        ResponseSchema(200, "Successful classification with entire distribution", InferenceDistributionResponseSchema),
        ResponseSchema(401, "Authentication failed"),
        ResponseSchema(404, "Model not found"),
        ResponseSchema(422, "Too many names"),
        ResponseSchema(500, "Internal server error"),
    ]
)
@jwt_required()
@error_handler
def classification_disitribution_route():
    current_app.logger.info(f"Received classification distribution request.")

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

    increment_request_counter(user_id=user_id, model_id=model_id, name_amount=len(request_data.names))

    current_app.logger.info("Successfully classified names.")
    return success_response(data=response_data)
