from dataclasses import dataclass
import json
from flask import Flask
from pydantic import BaseModel


OPENAPI_FLASK_ENV = "OPENAPI_SPEC"


@dataclass
class OAIRequest:
    model: BaseModel
    required: bool = True


@dataclass
class OAIResponse:
    status_code: int
    description: str
    model: BaseModel = None



class OpenAIGenerator:
    def __init__(self, app: Flask):
        self.openapi_routes = {}
        self.init_app(app)

    def init_app(self, app: Flask):
        if OPENAPI_FLASK_ENV not in app.config:
            raise ValueError(f"Basic openapi configuration must be provided under app.config['{OPENAPI_FLASK_ENV}'].")

        app.openai_generator = self

        original_add_url_rule = app.add_url_rule

        def wrapped_add_url_rule(rule, endpoint=None, view_func=None, **options):
            if hasattr(view_func, "_registered"):
                methods = options.get("methods", ["GET"])
                description = getattr(view_func, "_description", None)
                tags = getattr(view_func, "_tags", None)
                request_model = getattr(view_func, "_request_model", None)
                response_models = getattr(view_func, "_response_models", None)
                self.collect(
                    rule=rule,
                    methods=methods,
                    description=description,
                    tags=tags,
                    request_model=request_model,
                    response_models=response_models
                )

            return original_add_url_rule(rule, endpoint, view_func, **options)

        app.add_url_rule = wrapped_add_url_rule

    def collect(self, rule, methods: list[str], description: str, tags: list[str],  response_models: list[OAIResponse], request_model: OAIRequest = None):
        method = methods[0].lower()
        route_spec =  {
            "tags": tags,
            "description": description,
            "summary": "what should come here?",
            "operationId": "and here?",
        }
        
        if request_model:
            route_spec["requestBody"] = request_model.model_json_schema()
        
        route_spec["responses"] = {}
        for response in response_models:
            status_code = response.status_code
            route_spec["responses"][status_code] = {
                "description": response.description
            }
            if response.model:
                route_spec["responses"][status_code]["content"] = {
                    "application/json": {
                        "schema": response.model.model_json_schema()
                    }
                }

        self.openapi_routes[rule] = {
            method: route_spec
        }

    def save_openapi_spec(self, app, filename="./openapi.json", format: str = "json"):
        app.config[OPENAPI_FLASK_ENV]["paths"] = self.openapi_routes

        with open(filename, "w") as f:
            if format == "json":
                json.dump(app.config[OPENAPI_FLASK_ENV], f, indent=4)
            elif format == "yml" or format == "yaml":
                # TODO convert to yaml and save
                json.dump(app.config[OPENAPI_FLASK_ENV], f, indent=4)
            else:
                raise ValueError("Valid formats to save openapi spec. are: json, yaml")


def set_openapi_base_config(app: Flask, base_config: dict | str):
    if isinstance(base_config, str) and base_config.endswith("."):
        openapi_base_config = json.load(open(base_config, "r"))
    elif isinstance(base_config, dict):
        openapi_base_config = base_config
    else:
        raise ValueError("Argument 'base_config' must be either a dict or a path to a .json file.")
    
    app.config[OPENAPI_FLASK_ENV] = openapi_base_config



def register_route(description: str, tags: list[str], responses: list[OAIResponse], request: OAIRequest = None):
    def decorator(func):
        func._registered = True
        func._description = description
        func._tags = tags
        func._request_model = request
        func._response_models = responses
        return func
    return decorator
