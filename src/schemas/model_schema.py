from pydantic import BaseModel


class AddModelSchema(BaseModel):
    """ Schema to validate the /models POST request data """ 
    name: str
    nationalities: list[str]


class DeleteModelSchema(BaseModel):
    """ Schema to validate the /models POST request data """ 
    names: list[str]


class N2EModel(BaseModel):
    """ Schema to validate N2E Model data """ 
    name: str
    nationalities: list[str]
    accuracy: float | None
    scores: list[float] | None
    creationTime: str


class GetModelsResponseSchema(BaseModel):
    """ Schema to validate the /models GET response data """ 
    customModels: list[N2EModel]
    defaultModels: list[N2EModel]
