from pydantic import BaseModel, RootModel


class InferenceSchema(BaseModel):
    """ Schema to validate name classification request data """
    modelName: str
    names: list[str]
    getDistribution: bool

    class Config:
        json_schema_extra = {
            "example": {
                "modelName": "chinese_german_french",
                "names": ["Cixin Liu", "werner heisenberg", "Jules Verne"],
                "getDistribution": False
            }
        }

class InferenceResponseSchema(RootModel):
    """ Schema to validate the /classify POST response data """ 
    root: dict[str, tuple[str, float]]

    class Config:
        json_schema_extra = {
            "example": {
                "Cixin Liu": ["chinese", 0.91],
                "werner heisenberg": ["german", 0.87],
                "Jules Verne": ["french", 0.75]
            }
        }


class InferenceDistributionResponseSchema(RootModel):
    """ Schema to validate the /classify POST response data with 'getDistribution' set to 'True' """ 
    root: dict[str, dict[str, float]]

    class Config:
        json_schema_extra = {
            "example": {
                "Cixin Liu": {"chinese": 0.91, "german": 0.05, "french": 0.04},
                "werner heisenberg": {"chinese": 0.06, "german": 0.87, "french": 0.07},
                "Jules Verne": {"chinese": 0.2, "german": 0.13, "french": 0.75},
            }
        }
