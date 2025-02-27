from flask_spec_gen import openapi_generator as og
from schemas.util_schema import NationalitiesSchema
from utils import get_nationalities
from flask import Blueprint, current_app
from utils import success_response, get_nationalities


util_routes = Blueprint("utils", __name__)


@util_routes.route("/nationalities", methods=["GET"])
@og.register_route(
    summary="Get nationalities.",
    description="Returns a list of all available nationalities (49) and nationality groups (8) along with the amount of samples we have of them in our dataset.",
    tags=["Miscellaneous"],
    responses=[
        og.OAIResponse(200, "Successfully retrieved nationalities", NationalitiesSchema),
        og.OAIResponse(500, "Internal server error"),
    ],
)
def get_nationalities_route():
    """ Route for model requests """

    current_app.logger.info(f"Received nationality data request.")

    nationalities = get_nationalities()

    current_app.logger.info("Successfully loaded nationalities.")
    return success_response(data=nationalities)
