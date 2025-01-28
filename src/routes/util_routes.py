from openapi_gen import RequestSchema, ResponseSchema, with_openapi
from utils import get_nationalities
from flask import Blueprint, current_app
from utils import success_response, get_nationalities
from schemas.util_schema import NationalitiesSchema
from flask import current_app


util_routes = Blueprint("utils", __name__)


@util_routes.route("/nationalities", methods=["GET"])
@with_openapi(
    description="Returns a list of all available nationalities (49) and nat. groups (8) along with the amount of samples we have of them in our dataset.",
    tags=["Utilities"],
    responses=[
        ResponseSchema(200, "Successfully retrieved models", NationalitiesSchema),
        ResponseSchema(500, "Internal server error"),
    ],
)
def get_nationalities_route():
    """ Route for model requests """

    current_app.logger.info(f"Received nationality data request.")

    nationalities = get_nationalities()

    current_app.logger.info("Successfully loaded nationalities.")
    return success_response(data=nationalities)
