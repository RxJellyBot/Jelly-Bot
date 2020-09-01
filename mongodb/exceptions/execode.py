"""Exceptions related to executions about Execode."""
from typing import Union, Set

from flags import Execode, ExecodeCollationFailedReason


class NoCompleteActionError(Exception):
    """Raised if no corresponding action completion process."""

    def __init__(self, action: Execode):
        self._action = action
        super().__init__(f"No complete action implemented for {action}.")

    @property
    def action(self) -> Execode:
        """
        Get the action that raises this error.

        :return: action that raises this error
        """
        return self._action


class ExecodeCollationError(Exception):
    """Raised if any error occurred during Execode parameter collation."""

    def __init__(self, action: Execode, key: Union[str, Set[str]],
                 err_code: ExecodeCollationFailedReason, inner_ex: Exception = None):
        self._err_code = err_code

        super().__init__(
            f"Error occurred during collation of action {str(action)} at {key}. (Err Reason {err_code}, {inner_ex})")

    @property
    def err_code(self) -> ExecodeCollationFailedReason:
        """
        Get the reason of the failure.

        :return: reason of the failure
        """
        return self._err_code
