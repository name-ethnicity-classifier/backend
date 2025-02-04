from dataclasses import dataclass
import json
import yaml
from flask import Flask, jsonify, send_file, render_template_string
from pydantic import BaseModel

OPENAPI_FLASK_ENV = "OPENAPI_SPEC"
SWAGGER_UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui.min.css"/>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.11.1/swagger-ui-bundle.min.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui'
            });
        }
    </script>
</body>
</html>
"""

@dataclass
class OAIRequest:
    description: str
    model: BaseModel = None

@dataclass
class OAIResponse:
    status_code: int
    description: str
    model: BaseModel = None

class OpenAIGenerator:
    def __init__(self, app: Flask):
        self.openapi_routes = {}
        self.components = {}
        self.openapi_specification = {}

        self._init_app(app)

    def _init_app(self, app: Flask):
        if OPENAPI_FLASK_ENV not in app.config:
            raise ValueError(f"Basic OpenAPI configuration must be provided under app.config['{OPENAPI_FLASK_ENV}'].")
        
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
            return jsonify(self.openapi_specification)

        @app.route("/swagger")
        def serve_swagger_ui():
            return render_template_string(SWAGGER_UI_TEMPLATE)

    def _collect(self, rule, methods, view_func):
        method = methods[0].lower()
        
        route_spec = {
            "tags": view_func._tags,
            "description": view_func._description,
            "summary": view_func._description,
            "operationId": view_func.__name__,
            "responses": {}
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

        self.openapi_routes.setdefault(rule, {})[method] = route_spec

    def _replace_defs(self, schema: dict) -> dict:
        if "properties" not in schema:
            return schema
        
        for prop_name in schema["properties"]:
            prop = schema["properties"][prop_name]

            if "items" in prop and "$ref" in prop["items"]:
                if prop["items"]["$ref"].split("/")[1] == "$defs":
                    component_name = prop["items"]["$ref"].split("/")[-1]
                    schema["properties"][prop_name]["items"]["$ref"] = f"#/components/schemas/{component_name}"

            if "$ref" in prop:
                if prop["$ref"].split("/")[1] == "$defs":
                    component_name = prop["$ref"].split("/")[-1]
                    schema["properties"][prop_name]["$ref"] = f"#/components/schemas/{component_name}"

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
                prop = schema["properties"][prop_name]
                if "items" in prop and "$ref" in prop["items"]:
                    if prop["items"]["$ref"].split("/")[1] == "$defs":
                        component_name = prop["items"]["$ref"].split("/")[-1]
                        schema["properties"][prop_name]["items"]["$ref"] = f"#/components/schemas/{component_name}"
                if "$ref" in prop:
                    if prop["$ref"].split("/")[1] == "$defs":
                        component_name = prop["$ref"].split("/")[-1]
                        schema["properties"][prop_name]["$ref"] = f"#/components/schemas/{component_name}"

        self.components[model_name] = schema

        return {"$ref": f"#/components/schemas/{model_name}"}

    def _save_openapi_spec(self, spec: dict, file_format: str = "both"):
        valid_formats = ["yml", "yaml", "json", "both"]
        if file_format not in valid_formats:
            raise ValueError(f"Valid formats are: {', '.join(valid_formats)}")
        
        if file_format == "json" or file_format == "both":
            json.dump(spec, open("openapi.json", "w"), indent=4)
        if file_format in ["yml", "yaml"] or file_format == "both":
            yaml.dump(spec, open("openapi.yml", "w"), default_flow_style=False)

    def generate_openapi_spec(self, app: Flask, save_to_file: bool = True, file_format: str = "both"):
        spec = app.config[OPENAPI_FLASK_ENV]
        spec["paths"] = self.openapi_routes
        spec["components"] = {"schemas": self.components}

        if save_to_file:
            self._save_openapi_spec(spec, file_format=file_format)
        
        self.openapi_specification = spec


def register_route(description: str, tags: list[str], requests: list[OAIRequest] = None, responses: list[OAIResponse] = None):
    def decorator(func):
        func._registered = True
        func._description = description
        func._tags = tags
        func._request_models = requests if requests else []
        func._response_models = responses if responses else []
        return func
    return decorator
