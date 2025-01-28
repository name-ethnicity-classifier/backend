from pydantic import BaseModel, RootModel
from typing import Optional


class AddModelSchema(BaseModel):
    """ Schema to validate the /models POST request data """ 
    name: str
    description: Optional[str] = None
    nationalities: list[str]


class DeleteModelSchema(BaseModel):
    """ Schema to validate the /models POST request data """ 
    names: list[str]


class N2EModel(BaseModel):
    """ Schema to validate N2E Model data """ 
    name: str
    description: Optional[str] = None
    nationalities: list[str]
    accuracy: float | None
    scores: list[float] | None
    creationTime: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "chinese_german_french",
                "description": "Classifies between 3 ethnicities.",
                "nationalities": ["chinese", "german", "french"],
                "accuracy": 0.87,
                "scores": [0.97, 0.85, 0.81],
                "creationTime": "01-01-2025T07:21:00"
            }
        }


class ModelsResponseSchema(BaseModel):
    """ Schema to validate the /models GET response data """ 
    customModels: list[N2EModel]
    defaultModels: list[N2EModel]

    class Config:
        json_schema_extra = {
            "example": {
                "customModels": [
                    N2EModel.model_json_schema(ref_template="#/components/schemas/{model}")["example"]
                ],
                "defaultModels": [
                    {
                        "name": "spanish_else",
                        "description": "Classifies between spanish or not spanish.",
                        "nationalities": ["spanish", "else"],
                        "accuracy": 0.92,
                        "scores": [0.89, 0.95],
                        "creationTime": "01-01-2025T06:21:00"
                    }
                ]
            }
        }


class DefaultModelsResponseSchema(RootModel):
    """ Schema to validate the /default-models GET response data """ 
    root: list[N2EModel]

    class Config:
        json_schema_extra = {
            "example": [
                {
                    "name": "spanish_else",
                    "description": "Classifies between spanish or not spanish.",
                    "nationalities": ["spanish", "else"],
                    "accuracy": 0.92,
                    "scores": [0.89, 0.95],
                    "creationTime": "01-01-2025T06:21:00"
                }
            ]
        }
