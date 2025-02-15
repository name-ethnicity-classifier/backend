from dataclasses import dataclass
import json
import os
import yaml
from flask import Flask, jsonify, render_template_string, send_from_directory
from pydantic import BaseModel
from flask_spec_gen.models import *


with open(os.path.join(os.path.dirname(__file__), "static/swagger-ui.html"), "r") as f:
    SWAGGER_UI_TEMPLATE = f.read()


@dataclass
class OAIRequest:
    description: str
    model: BaseModel = None

@dataclass
class OAIResponse:
    status_code: int
    description: str
    model: BaseModel = None


class OpenAPIGenerator:

    def __init__(self, app: Flask, base_config: dict):
        self.base_config = base_config
        self.openapi_specification = {}

        self.served_specification = None

        self._init_app(app)

    def _read_and_validate_base_config(self):
        config = Config(**self.base_config)

        self.openapi_specification = {
            "openapi": config.openapi,
            "info": config.info.model_dump(mode="json", exclude_none=True),
            "servers": [server.model_dump(mode="json", exclude_none=True) for server in config.servers],
            "tags": [],
            "components": {
                "schemas": {}
            },
            "paths": {}
        }

        if config.tags and len(config.tags) > 0:
            self.openapi_specification["tags"] = [tag.model_dump(mode="json", exclude_none=True) for tag in config.tags]
            
        if config.securitySchemes and len(config.securitySchemes) > 0:
            securitySchemes = {}
            for name in config.securitySchemes:
                securitySchemes[name] = config.securitySchemes[name].model_dump(mode="json", exclude_none=True)
            self.openapi_specification["components"]["securitySchemes"] = securitySchemes

    def _init_app(self, app: Flask):
        self._read_and_validate_base_config()
        
        app.openapi_generator = self
        original_add_url_rule = app.add_url_rule

        def wrapped_add_url_rule(rule, endpoint=None, view_func=None, **options):
            if hasattr(view_func, "_registered"):
                methods = options.get("methods", ["GET"])
                self._collect(rule, methods, view_func)
            return original_add_url_rule(rule, endpoint, view_func, **options)

        app.add_url_rule = wrapped_add_url_rule
        
        @app.route("/openapi.json")
        def serve_openapi_json():
            return jsonify(self.served_specification)

        if self.base_config["swaggerEnabled"]:
            @app.route("/swagger-static/<path:filename>")
            def serve_swagger_static(filename):
                static_dir = os.path.join(os.path.dirname(__file__), "static/swagger-ui")
                return send_from_directory(static_dir, filename)

            @app.route(f"/{self.base_config['swaggerUrl']}")
            def serve_swagger_ui():
                return render_template_string(SWAGGER_UI_TEMPLATE)

    def _collect(self, rule, methods, view_func):
        method = methods[0].lower()
        
        route_spec = {
            "tags": view_func._tags,
            "description": view_func._description,
            "summary": view_func._description,
            "operationId": view_func.__name__,
            "responses": {},
            "security": [
                {
                    "BearerAuth": []
                }
            ]
        }

        if view_func._request_models:
            route_spec["requestBody"] = {
                "content": {}
            }
            for request in view_func._request_models:
                if request.model:
                    schema_ref = self._get_schema_ref(request.model.model_json_schema())
                    route_spec["requestBody"]["content"]["application/json"] = {
                        "schema": schema_ref
                    }
        
        for response in view_func._response_models:
            response_spec = {"description": response.description}
            if response.model:
                schema_ref = self._get_schema_ref(response.model.model_json_schema())
                response_spec["content"] = {"application/json": {"schema": schema_ref}}
            route_spec["responses"][str(response.status_code)] = response_spec

        self.openapi_specification["paths"].setdefault(rule, {})[method] = route_spec
    
    def _update_schema_ref(self, schema: dict) -> dict:
        if "items" in schema and "$ref" in schema["items"]:
            if schema["items"]["$ref"].split("/")[1] == "$defs":
                component_name = schema["items"]["$ref"].split("/")[-1]
                schema["items"]["$ref"] = f"#/components/schemas/{component_name}"
        if "$ref" in schema:
            if schema["$ref"].split("/")[1] == "$defs":
                component_name = schema["$ref"].split("/")[-1]
                schema["$ref"] = f"#/components/schemas/{component_name}"

        return schema

    def _get_schema_ref(self, model: dict):
        schema = model
        model_name = model["title"]

        if "$defs" in schema:
            for local_definition in schema["$defs"]:
                local_definition_model = schema["$defs"][local_definition]
                _ = self._get_schema_ref(local_definition_model)

            del schema["$defs"]

        if "properties" in schema:
            for prop_name in schema["properties"]:
                schema["properties"][prop_name] = self._update_schema_ref(schema["properties"][prop_name])
        else:
            schema = self._update_schema_ref(schema)

        self.openapi_specification["components"]["schemas"][model_name] = schema

        return {"$ref": f"#/components/schemas/{model_name}"}

    def save_to_file(self, file_format: str = "both"):
        valid_formats = ["yml", "yaml", "json", "both"]
        if file_format not in valid_formats:
            raise ValueError(f"Valid formats are: {', '.join(valid_formats)}")
        
        if file_format == "json" or file_format == "both":
            json.dump(self.served_specification, open("openapi.json", "w"), indent=4)
        if file_format in ["yml", "yaml"] or file_format == "both":
            yaml.dump(self.served_specification, open("openapi.yml", "w"), default_flow_style=False)

    def generate(self, save_to_file: bool = True, format: str = "both"):
        self.served_specification = self.openapi_specification

        if save_to_file:
            self.save_to_file(format)


def register_route(description: str, tags: list[str], requests: list[OAIRequest] = None, responses: list[OAIResponse] = None):
    def decorator(func):
        func._registered = True
        func._description = description
        func._tags = tags
        func._request_models = requests if requests else []
        func._response_models = responses if responses else []
        return func
    return decorator



