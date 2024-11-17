from utils import get_nationalities
from flask import Blueprint, current_app
from utils import success_response, get_nationalities


util_routes = Blueprint("utils", __name__)


@util_routes.route("/nationalities", methods=["GET"])
def get_nationalities_route():
    """ Route for model requests """

    current_app.logger.info(f"Received nationality data request.")

    nationalities = get_nationalities()

    current_app.logger.info("Successfully loaded nationalities.")
    return success_response(data=nationalities)
