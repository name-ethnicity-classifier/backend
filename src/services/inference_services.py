from db.tables import  UserToModel
from db.database import db


def increment_request_counter(user_id: str, model_id: str) -> None:
    """
    Increments the 'request_count' value for certain model of a user.
    :param user_id: The user id who owns the model
    :param model_name: The model for which to increment the counter
    :return: None
    """

    user_to_model = UserToModel.query.filter_by(user_id=user_id, model_id=model_id).first()
    user_to_model.request_count += 1
    db.session.commit()
