from pydantic import BaseModel


class InferenceSchema(BaseModel):
    """ Schema to validate name classification request data """
    modelName: str
    names: list[str]
    getDistribution: bool
