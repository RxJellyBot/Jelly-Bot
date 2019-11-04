from flags import TokenAction, TokenActionCollationFailedReason


class NoCompleteActionError(Exception):
    def __init__(self, action: TokenAction):
        super().__init__(f"No complete action implemented for {action}.")


class TokenActionCollationError(Exception):
    def __init__(self,
                 action: TokenAction, key: str, err_code: TokenActionCollationFailedReason, inner_ex: Exception = None):
        super().__init__(
            f"Error occurred during collation of action {str(action)} at {key}. (Err Reason {err_code}, {inner_ex})")
