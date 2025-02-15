from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Optional, Any


class ContactInfo(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    email: Optional[str] = None

    class Config:
        json_encoders = {HttpUrl: str}


class LicenseInfo(BaseModel):
    name: str
    url: Optional[HttpUrl] = None

    class Config:
        json_encoders = {HttpUrl: str}


class ServerInfo(BaseModel):
    url: HttpUrl
    description: Optional[str] = None

    class Config:
        json_encoders = {HttpUrl: str}


class TagInfo(BaseModel):
    name: str
    description: Optional[str] = None


class SecurityScheme(BaseModel):
    type: str
    description: Optional[str] = None
    name: Optional[str] = None
    in_: Optional[str] = Field(None, alias="in")
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional[Dict[str, Any]] = None
    openIdConnectUrl: Optional[HttpUrl] = None


class ExternalDocs(BaseModel):
    description: Optional[str] = None
    url: HttpUrl

    class Config:
        json_encoders = {HttpUrl: str}


class Info(BaseModel):
    title: str
    version: str
    description: str
    termsOfService: Optional[str]
    contact: Optional[ContactInfo] = None
    license: Optional[LicenseInfo] = None


class Config(BaseModel):
    openapi: str = Field(..., pattern=r"^3\.\d+\.\d+$") 
    info: Info
    servers: list[ServerInfo]
    tags: Optional[List[TagInfo]] = None
    externalDocs: Optional[ExternalDocs] = None
    securitySchemes: Optional[Dict[str, SecurityScheme]] = None
    swaggerUrl: Optional[str] = None
    swaggerEnabled: bool = True