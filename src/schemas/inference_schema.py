from pydantic import BaseModel, RootModel


class InferenceSchema(BaseModel):
    """ Schema to validate name classification request data """
    modelName: str
    names: list[str]
    getDistribution: bool


class InferenceResponseSchema(RootModel):
    """ Schema to validate the /classify POST response data """ 
    root: dict[str, tuple[str, float]]


class InferenceDistributionResponseSchema(RootModel):
    """ Schema to validate the /classify POST response data with 'getDistribution' set to 'True' """ 
    root: dict[str, dict[str, float]]


    # Response schema: { <name: str>: {<class 1: str>: <confidence: float>, <class 2: str>: <confidcence: float>}, ... }
