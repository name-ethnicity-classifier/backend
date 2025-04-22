from pydantic import BaseModel


class LoginSchema(BaseModel):
    """ Schema to validate the /login POST request data """ 
    email: str
    password: str
    

class SignupSchema(BaseModel):
    """ Schema to validate the /signup POST request data """
    email: str
    password: str
    name: str
    role: str
    consented: bool
    usageDescription: str


class UpdateUsageDescriptionSchema(BaseModel):
    """ Schema to validate the /update-usage-description POST request data """
    usageDescription: str


class DeleteUserSchema(BaseModel):
    """ Schema to validate the /delete-user POST request data """
    password: str

