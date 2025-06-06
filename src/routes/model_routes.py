from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas.model_schema import AddModelSchema, DefaultModelsResponseSchema, DeleteModelSchema, ModelsResponseSchema, N2EModel
from services.model_services import add_model, get_models, get_default_models, delete_models
from services.user_services import check_user_existence, check_user_restriction
from utils import success_response
from errors import error_handler
from flask_spec_gen import openapi_generator as og


model_routes = Blueprint("models", __name__)


@model_routes.route("/models", methods=["POST"])
@jwt_required()
@error_handler
def add_model_route():
    """ Route for model requests """

    current_app.logger.info(f"Received model request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)
    check_user_restriction(user_id)

    request_data = AddModelSchema(**request.json)
    add_model(user_id, request_data)

    current_app.logger.info("Successfully added model data to database.")
    return success_response(message="Model added successfully.")


@model_routes.route("/models", methods=["DELETE"])
@jwt_required()
@error_handler
def delete_models_route():
    """ Route for deleting models """

    current_app.logger.info(f"Received model deletion request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    request_data = DeleteModelSchema(**request.json)
    delete_models(user_id, request_data)
    
    current_app.logger.info(f"Successfully deleted model(-s) from user with user id {user_id}.")
    return success_response(message="Model(-s) deleted successfully.")


@model_routes.route("/models", methods=["GET"])
@og.register_route(
    summary="Get all models.",
    description="Using this endpoint you can receive all your custom and N2Es default models.",
    tags=["Model Management"],
    responses=[
        og.OAIResponse(200, "Successfully retrieved models.", ModelsResponseSchema),
        og.OAIResponse(401, "Authentication failed"),
        og.OAIResponse(500, "Internal server error"),
    ],
)
@jwt_required()
@error_handler
def get_models_route():
    """ Route for requesting model data """

    current_app.logger.info(f"Received model retrieval request.")

    user_id = get_jwt_identity()
    check_user_existence(user_id)

    model_data = get_models(user_id)
    ModelsResponseSchema(**model_data)

    current_app.logger.info(f"Successfully received model data from user with user id {user_id}.")
    return success_response(
        data=model_data
    )


@model_routes.route("/default-models", methods=["GET"])
@og.register_route(
    summary="Get all default models.",
    description="Using this endpoint you can receive all models that N2E provides by default.",
    tags=["Model Management"],
    responses=[
        og.OAIResponse(200, "Successfully retrieved models.", DefaultModelsResponseSchema),
        og.OAIResponse(500, "Internal server error"),
    ],
)
@error_handler
def get_default_models_route():
    """ Route for requesting default model data """

    current_app.logger.info(f"Received default model retrieval request.")

    default_model_data = get_default_models()
    DefaultModelsResponseSchema(default_model_data)

    current_app.logger.info(f"Successfully received default model data.")
    return success_response(
        data=default_model_data
    )
