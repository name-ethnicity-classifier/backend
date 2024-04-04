
class CustomError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class InferenceError(Exception):
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message

