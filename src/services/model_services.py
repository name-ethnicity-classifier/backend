import hashlib
from errors import CustomError
from schemas.model_schema import AddModelSchema, DeleteModelSchema
from db.tables import Model, UserToModel
from db.database import db
from utils import check_requested_nationalities


def add_model(user_id: str, data: AddModelSchema) -> None:
    """
    Adds a new model row to the database
    :param user_id: User ID to which the model corresponds
    :param data: Actual model data
    """

    # 0 for normal nationality configuration, 1 for nationality groups (european, eastAsian, etc.)
    checked_nationalities = check_requested_nationalities(data.nationalities)

    # Is -1 if requested nationalities don't exist or are mixed with nationality groups
    if checked_nationalities == -1:
        raise CustomError(
            error_code="NATIONALITIES_INVALID",
            message=f"Requested nationalities (-groups) are invalid.",
            status_code=404,
        )

    existing_model_names = UserToModel.query.filter_by(user_id=user_id, name=data.name).all()
    if data.name in [model.name for model in existing_model_names]:
        raise CustomError(
            error_code="MODEL_NAME_EXISTS",
            message=f"Model with name '{data.name}' already exists for this user.",
            status_code=409,
        )

    # Sort nationalities
    nationalities = sorted(set(data.nationalities))
    model_id = hashlib.sha256(",".join(nationalities).encode()).hexdigest()[:20]

    same_model_exists = Model.query.filter_by(id=model_id).first()
    if not same_model_exists:
        new_model = Model(
            id=model_id,
            nationalities=nationalities,
            is_grouped=(checked_nationalities == 1),
            is_custom=True
        )
        db.session.add(new_model)

    user_to_model_entry = UserToModel(
        model_id=model_id,
        user_id=user_id,
        name=data.name
    )
    db.session.add(user_to_model_entry)

    db.session.commit()


def get_models(user_id: str) -> dict:
    """
    Gets a questionnaire row from the database
    :param user_id: User ID from which to get the questionnaire data
    :return: The questionnaire data row
    """

    # Get all default models
    default_models = Model.query.filter_by(is_custom=False).all()

    # Get all the users models from the user_to_model table
    user_model_relations = UserToModel.query.filter_by(user_id=user_id)
    user_model_ids = [relation.model_id for relation in user_model_relations]

    # Get all custom models
    custom_models = db.session.query(Model).filter(Model.id.in_(user_model_ids)).all()

    default_model_data = []
    for model in default_models:
        model = model.to_dict()
        default_model_data.append({
            "name": model["id"],
            "accuracy": model["accuracy"],
            "nationalities": model["nationalities"],
            "scores": model["scores"],
            "creationTime": model["creation_time"],
            "isCustom": model["is_custom"]
        })

    custom_model_data = []
    for model in custom_models:
        model = model.to_dict()
        custom_model_data.append({
            "name": user_model_relations.filter_by(model_id=model["id"]).first().name,
            "accuracy": model["accuracy"],
            "nationalities": model["nationalities"],
            "scores": model["scores"],
            "creationTime": model["creation_time"],
            "isCustom": model["is_custom"]
        })

    return {
        "defaultModels": default_model_data,
        "customModels": custom_model_data
    }


def delete_models(user_id: str, data: DeleteModelSchema) -> None:
    """
    Deletes a model-user relation from the database. This does not delete the model itself since 
    it can be shared across multiple users.
    :param user_id: User ID of which to delete the model
    :param model_name: Name of the model which to delete
    """

    # Get all the users models from the user_to_model table
    existing_models = UserToModel.query.filter(UserToModel.user_id == user_id, UserToModel.name.in_(data.names)).all()

    for model in existing_models:
        db.session.delete(model)

    db.session.commit()


def get_model_id_by_name(user_id: str, model_name: str) -> str:
    """
    Retrieves the model ID given a model name
    :param user_id: The user which searches for the model by name
    :param model_name: The name the user gave the model
    :return: The model ID
    """

    models = UserToModel.query.filter_by(user_id=user_id, name=model_name).first()
    
    if not models:
        raise CustomError(
            error_code="MODEL_DOES_NOT_EXIST",
            message=f"Model with name '{model_name}' does not exist for this user.",
            status_code=404,
        )
    
    return models.model_id
