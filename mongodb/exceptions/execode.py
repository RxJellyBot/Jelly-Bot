from flags import Execode, ExecodeCollationFailedReason


class NoCompleteActionError(Exception):
    def __init__(self, action: Execode):
        self._action = action
        super().__init__(f"No complete action implemented for {action}.")

    @property
    def action(self) -> Execode:
        return self._action


class ExecodeCollationError(Exception):
    def __init__(self,
                 action: Execode, key: str, err_code: ExecodeCollationFailedReason, inner_ex: Exception = None):
        super().__init__(
            f"Error occurred during collation of action {str(action)} at {key}. (Err Reason {err_code}, {inner_ex})")
