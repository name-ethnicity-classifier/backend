from functools import wraps
from pydantic import BaseModel
from dataclasses import dataclass
import yaml
from globals import api_config


@dataclass
class RequestSchema:
    model: BaseModel
    required: bool = True


@dataclass
class ResponseSchema:
    status_code: int
    description: str
    model: BaseModel = None


def openapi_spec(description: str, tags: list[str], responses: list[ResponseSchema], request_schema: RequestSchema = None) -> str:
    spec = {}

    if tags:
        spec["tags"] = tags

    if "schemas" not in api_config["components"]:
        api_config["components"]["schemas"] = {}

    if request_schema:
        schema, refs = process_pydantic_schema(request_schema.model.model_json_schema(ref_template="#/components/schemas/{model}"))

        api_config["components"]["schemas"][request_schema.model.__name__] = schema
        for name in refs:
           api_config["components"]["schemas"][name] = refs[name] 

        spec["parameters"] = [{
            "name": "body",
            "in": "body",
            "required": request_schema.required,
            "schema": f"#/components/schemas/{request_schema.model.__name__}"
        }]

    spec["responses"] = {}
    for response in responses:
        status_code = response.status_code
        spec["responses"][status_code] = {"description": response.description}
        if response.model:

            schema, refs = process_pydantic_schema(response.model.model_json_schema())
            print(refs)

            api_config["components"]["schemas"][response.model.__name__] = schema
            for name in refs:
                api_config["components"]["schemas"][name] = refs[name]


            #api_config["components"]["schemas"][response.model.__name__] = response.model.model_json_schema(ref_template="#/components/schemas/{model}")

            spec["responses"][status_code]["content"] = {
                "application/json": {
                    "schema": f"#/components/schemas/{response.model.__name__}"
                }
            }

    spec_string = yaml.dump(spec, default_flow_style=False)
    spec_string = f"{description}\n---\n{spec_string}"

    # print(spec_string)

    return spec_string


def process_pydantic_schema(schema: dict) -> tuple[dict, dict]:
    """
    Processes a Pydantic schema to replace $defs references with #/components/schemas/ references
    and extracts the $defs content.

    Args:
        schema (dict): The Pydantic model's JSON schema.

    Returns:
        tuple: A tuple containing the updated schema and a dictionary of extracted $defs.
    """
    # Make a deep copy of the schema to avoid modifying the original
    import copy
    updated_schema = copy.deepcopy(schema)
    extracted_defs = {}

    # Helper function to recursively update $ref fields
    def update_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and "$defs" in value:
                    # Extract the model name from the $defs reference
                    model_name = value.split("/")[-1]

                    # Extract the definition and update the reference
                    if model_name in schema.get("$defs", {}):
                        extracted_defs[model_name] = schema["$defs"][model_name]
                        obj[key] = f"#/components/schemas/{model_name}"
                else:
                    update_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                update_refs(item)

    # Start processing the schema
    update_refs(updated_schema)

    # Remove $defs from the schema if it exists
    if "$defs" in updated_schema:
        del updated_schema["$defs"]

    return updated_schema, extracted_defs



def with_openapi(description, tags, responses, request_schema = None):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapped.__doc__ = openapi_spec(
            description=description,
            tags=tags,
            request_schema=request_schema,
            responses=responses,
        )
        return wrapped
    return decorator

