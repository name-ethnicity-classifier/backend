from functools import wraps
import traceback
from flask import current_app
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError 
from utils import error_response


class GeneralError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class InferenceError(Exception):
    def __init__(self, error_code: str, message: str, status_code: str):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def error_handler(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            current_app.logger.error(f"Validation error: {e}")
            return error_response("VALIDATION_ERROR", str(e), 400)
        except GeneralError as e:
            current_app.logger.error(f"General error: {e.message}")
            return error_response(e.error_code, e.message, e.status_code)
        except InferenceError as e:
            current_app.logger.error(f"Inference error: {e.message}")
            return error_response(e.error_code, e.message, e.status_code)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {e}")
            return error_response("UNEXPECTED_ERROR", "An unexpected error occurred.", 500)
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {e}. Traceback:\n{traceback.format_exc()}")
            return error_response("UNEXPECTED_ERROR", "An unexpected error occurred.", 500)
    return wrapper
