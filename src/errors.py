class CustomError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class ModelError(CustomError):
    def __init__(self, error_code: str, message: str, status_code: int):
        super().__init__(error_code, message, status_code)

class ClassificationError(CustomError):
    def __init__(self, error_code: str, message: str, status_code: int):
        super().__init__(error_code, message, status_code)

class LoginError(CustomError):
    def __init__(self, error_code: str, message: str, status_code: int):
        super().__init__(error_code, message, status_code)

class SignupError(CustomError):
    def __init__(self, error_code: str, message: str, status_code: int):
        super().__init__(error_code, message, status_code)
