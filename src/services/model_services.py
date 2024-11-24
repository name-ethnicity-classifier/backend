from sqlalchemy import and_, or_
from errors import GeneralError
from schemas.model_schema import AddModelSchema, DeleteModelSchema
from db.tables import Model, UserToModel
from db.database import db
from utils import check_requested_nationalities, generate_model_id


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
        raise GeneralError(
            error_code="NATIONALITIES_INVALID",
            message=f"Requested nationalities (-groups) are invalid.",
            status_code=404
        )

    custom_models_name_name = (
        db.session.query(UserToModel)
        .filter(UserToModel.user_id == user_id, UserToModel.name == data.name)
        .first()
    )
    public_models_same_name = (
        db.session.query(Model)
        .filter(Model.is_public == True, Model.public_name == data.name)
        .first()
    )

    if custom_models_name_name is not None or public_models_same_name is not None:
        raise GeneralError(
            error_code="MODEL_NAME_EXISTS",
            message=f"Model with name '{data.name}' already exists for this user.",
            status_code=409,
        )

    model_id = generate_model_id(data.nationalities)
    same_model = Model.query.filter_by(id=model_id).first()

    if not same_model:
        new_model = Model(
            id=model_id,
            nationalities=sorted(set(data.nationalities)),
            is_grouped=(checked_nationalities == 1)
        )
        db.session.add(new_model)

    user_to_model_entry = UserToModel(
        model_id=model_id,
        user_id=user_id,
        name=data.name,
        description=data.description
    )
    db.session.add(user_to_model_entry)
    db.session.commit()


def get_default_models() -> dict:
    """
    Fetches all public default models from the database
    :return: All default models
    """

    # Get all default models
    default_models = Model.query.filter_by(is_public=True).all()

    default_model_data = []
    for model in default_models:
        model = model.to_dict()
        default_model_data.append({
            "name": model["public_name"],
            "accuracy": model["accuracy"],
            "nationalities": model["nationalities"],
            "scores": model["scores"],
            "creationTime": model["creation_time"],
        })

    return default_model_data
    

def get_models(user_id: str) -> dict:
    """
    Fetches all models a user has access to from the database
    :param user_id: User ID from which to get the model data
    :return: Users model data
    """

    # Get all the users models from the user_to_model table
    user_model_relations = UserToModel.query.filter_by(user_id=user_id)
    user_model_ids = [relation.model_id for relation in user_model_relations]

    models = (
        db.session.query(Model)
        .filter(Model.id.in_(user_model_ids))
        .order_by(Model.creation_time.desc())
        .all()
    )

    custom_model_data = []
    for model in models:

        # There might be multiple user_to_models pointing to the same model due to same classes
        for relation in user_model_relations.filter_by(model_id=model.id).all():
            custom_model_data.append({
                "name": relation.name,
                "description": relation.description,
                "accuracy": model.accuracy,
                "nationalities": model.nationalities,
                "scores": model.scores,
                "creationTime": model.creation_time,
            })

    return {
        "defaultModels": get_default_models(),
        "customModels": custom_model_data
    }


def delete_models(user_id: str, model_names: DeleteModelSchema) -> None:
    """
    Deletes a model-user relation from the database. This does not delete the model itself since 
    it can be shared across multiple users.
    :param user_id: User ID of which to delete the model
    :param data: Name of the model which to delete
    """

    # Get all the users models from the user_to_model table
    existing_models = UserToModel.query.filter(UserToModel.user_id == user_id, UserToModel.name.in_(model_names.names)).all()

    if len(existing_models) == 0:
        raise GeneralError(
            error_code="MODEL_DOES_NOT_EXIST",
            message=f"Model does not exist for this user.",
            status_code=404,
        )

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

    user_model = UserToModel.query.filter_by(user_id=user_id, name=model_name).first()
    if user_model:
        return user_model.model_id
    
    public_model = Model.query.filter_by(public_name=model_name).first()
    if public_model:
        return public_model.id
    
    raise GeneralError(
        error_code="MODEL_DOES_NOT_EXIST",
        message=f"Model with name '{model_name}' does not exist.",
        status_code=404,
    )
