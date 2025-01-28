from pydantic import BaseModel


class NationalitiesSchema(BaseModel):
    """ Schema of the /nationalities response """ 
    
    nationalities: dict[str, int]
    nationalityGroups: dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "nationalities": {
                    "british": 6134933,
                    "norwegian": 23920,
                    "indian": 90347,
                },
                "nationalitiyGroups": {
                    "african": 104673,
                    "angloAmerican": 112722,
                    "eastAsian": 631015,
                },
            }
        }
