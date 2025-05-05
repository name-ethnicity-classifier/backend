from flask import current_app
from datetime import date
from db.tables import  Model, User, UserQuota, UserToModel
from db.database import db
from errors import GeneralError


def increment_request_counter(user_id: str, model_id: str, name_amount: int):
    """
    Increments the 'request_count' value for certain model of a user.
    :param user_id: The user id who owns the model
    :param model_name: The model for which to increment the counter
    :param name_amount: Amonut of names requested for classification
    :return: None
    """

    user = User.query.filter_by(id=user_id).first()
    user.request_count += 1
    user.names_classified += name_amount
    db.session.commit()

    model = Model.query.filter_by(id=model_id).first()
    model.request_count += 1
    db.session.commit()
    
    user_to_model = UserToModel.query.filter_by(user_id=user_id, model_id=model_id).first()
    if user_to_model:
        user_to_model.request_count += 1
        db.session.commit()
    

def check_name_amount_and_quota(user_id: str, name_amount: int):
    """
    Checks if a user's classification request contains too many names or exceeds the daily quota limit.
    If its the first check of the day, reset the counter to 0,
    
    :param user_id: The user making the request.
    :param name_amount: The number of names to classify in the current request.
    """

    max_names = int(current_app.config["MAX_NAMES"])
    daily_limit = int(current_app.config["DAILY_QUOTA"])

    if name_amount > max_names:
        raise GeneralError(
            error_code="TOO_MANY_NAMES",
            message=f"Too many names (maximum {max_names}).",
            status_code=405
        )

    today = date.today()
    user_quota = UserQuota.query.filter_by(user_id=user_id).first()

    if not user_quota or user_quota.last_updated < today:
        # Reset quota if new day or create new record if none exists
        user_quota = user_quota or UserQuota(user_id=user_id)
        user_quota.name_count = 0
        user_quota.last_updated = today
        db.session.add(user_quota)
        db.session.commit()

    updated_name_count = user_quota.name_count + name_amount
    if updated_name_count > daily_limit:
        raise GeneralError(
            error_code="QUOTA_EXCEEDED",
            message=f"Daily quota of {daily_limit} names exceeded by {updated_name_count - daily_limit}.",
            status_code=405
        )


def update_name_quota(user_id: str, name_amount: int):
    """
    Updates a users name classificastion quota.

    :param user_id: The user making the request.
    :param name_amount: The number of names to classify in the current request.
    """

    user_quota = UserQuota.query.filter_by(user_id=user_id).first()
    user_quota.name_count += name_amount
    db.session.add(user_quota)
    db.session.commit()

