from flags import PreserializationFailedReason


class InvalidModelError(Exception):
    def __init__(self, model_name, message):
        super().__init__(f"Invalid model ({model_name}). Message: {message}")


class PreserializationFailedError(Exception):
    def __init__(self, reason: PreserializationFailedReason):
        super().__init__(f"Pre-serialization was failed. Reason: {reason}")
