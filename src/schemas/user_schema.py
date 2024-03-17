from pydantic import BaseModel


class LoginSchema(BaseModel):
    """ Model schema to validate the /login POST request data """ 
    email: str
    password: str


class SignupSchema(BaseModel):
    """ Model schema to validate the /signup POST request data """
    email: str
    password: str
    name: str
    role: str
    consented: bool