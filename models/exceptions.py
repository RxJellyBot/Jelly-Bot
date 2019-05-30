class InvalidModelError(Exception):
    def __init__(self, model_name, message):
        super().__init__(f"Invalid model ({model_name}). Message: {message}")