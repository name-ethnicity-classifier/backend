from pydantic import BaseModel


class AddModelSchema(BaseModel):
    """ Model schema to validate the /models POST request data """ 
    name: str
    nationalities: list[str]


class DeleteModelSchema(BaseModel):
    """ Model schema to validate the /models POST request data """ 
    names: list[str]


class ClassificationSchema(BaseModel):
    """ Model schema to validate the /classify POST request data """ 
    modelName: str
    names: list[str]
