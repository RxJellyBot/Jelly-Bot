"""Helpers to integrate the process of executing Execode."""
from typing import Set

from bson import ObjectId
from bson.errors import InvalidId

from flags import Platform, ExecodeCollationFailedReason, ExecodeCompletionOutcome, Execode
from JellyBot.api.static import param
from mixin import ClearableMixin
from models import ExecodeEntryModel, AutoReplyModuleModel
from mongodb.exceptions import NoCompleteActionError, ExecodeCollationError
from mongodb.factory import ChannelManager, AutoReplyManager, ProfileManager
from mongodb.factory.results import OperationOutcome
from mongodb.helper import UserDataIntegrationHelper

__all__ = ("ExecodeCompletor", "ExecodeParameterCollator", "ExecodeRequiredKeys",)


class ExecodeCompletor(ClearableMixin):
    """Helper to complete an Execode action."""

    @classmethod
    def clear(cls):
        ChannelManager.clear()
        AutoReplyManager.clear()
        ProfileManager.clear()

    # noinspection PyArgumentList
    @staticmethod
    def complete_execode(execode_entry: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        """
        Complete an Execode action.

        ``xparams`` will be checked during parameter collation. If there's any required keys missing, an
        :class:`ExecodeCollationError` with ``err_code`` as :class:`ExecodeCollationFailedReason.MISSING_KEY` will be
        raised.

        Currently supported :class:`Execode` action to complete:

        - :class:`Execode.AR_ADD`

        - :class:`Execode.REGISTER_CHANNEL`

        - :class:`Execode.INTEGRATE_USER_DATA`

        :param execode_entry: Execode entry to be completed
        :param xparams: parameters to be used to complete the Execode
        :return: outcome of the completion process
        :raises ExecodeCollationError: if there's any error occurred during parameter collation
        :raises NoCompleteActionError: if no corresponding complete action found
        """
        action = execode_entry.action_type
        xparams = ExecodeParameterCollator.collate_parameters(Execode(action), xparams)

        if action == Execode.AR_ADD:
            return ExecodeCompletor._excde_ar_add(execode_entry, xparams)

        if action == Execode.REGISTER_CHANNEL:
            return ExecodeCompletor._excde_register_channel(xparams)

        if action == Execode.INTEGRATE_USER_DATA:
            return ExecodeCompletor._excde_user_data_integration(execode_entry, xparams)

        raise NoCompleteActionError(action)

    @staticmethod
    def _excde_ar_add(action_model: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        cnl = ChannelManager.ensure_register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        if not cnl.success:
            return ExecodeCompletionOutcome.X_AR_REGISTER_CHANNEL

        add_conn_result = AutoReplyManager.add_conn(
            **action_model.data,
            **{AutoReplyModuleModel.ChannelOid.key: cnl.model.id,
               AutoReplyModuleModel.CreatorOid.key: action_model.creator_oid},
            from_db=True)

        if not add_conn_result.success:
            return ExecodeCompletionOutcome.X_AR_REGISTER_MODULE

        return ExecodeCompletionOutcome.O_OK

    @staticmethod
    def _excde_register_channel(xparams: dict) -> ExecodeCompletionOutcome:
        try:
            reg_result = ChannelManager.ensure_register(
                xparams[param.Execode.PLATFORM], xparams[param.Execode.CHANNEL_TOKEN])
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_ERROR

        if not reg_result.success:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_ENSURE_FAILED

        return ExecodeCompletionOutcome.O_OK

    @staticmethod
    def _excde_user_data_integration(action_model: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        try:
            result = UserDataIntegrationHelper.integrate(action_model.creator_oid, xparams[param.Execode.USER_OID])
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_INTEGRATION_ERROR

        if not result.is_success:
            if result == OperationOutcome.X_SRC_DATA_NOT_FOUND:
                return ExecodeCompletionOutcome.X_IDT_SOURCE_NOT_FOUND

            if result == OperationOutcome.X_DEST_DATA_NOT_FOUND:
                return ExecodeCompletionOutcome.X_IDT_TARGET_NOT_FOUND

            if result == OperationOutcome.X_SAME_SRC_DEST:
                return ExecodeCompletionOutcome.X_IDT_SOURCE_EQ_TARGET

            return ExecodeCompletionOutcome.X_IDT_INTEGRATION_FAILED

        return ExecodeCompletionOutcome.O_OK


class ExecodeParameterCollator:
    """Parameter collator of an Execode action."""

    @staticmethod
    def collate_parameters(action: Execode, xparams: dict) -> dict:
        """Collate the parameters ``xparams`` for an Execode action depending on the action type ``action``."""
        ExecodeParameterCollator._check_missing_keys(action, xparams)

        if action == Execode.AR_ADD:
            return ExecodeParameterCollator._execode_ar_add(action, xparams)

        if action == Execode.REGISTER_CHANNEL:
            return ExecodeParameterCollator._execode_conn_channel(xparams)

        if action == Execode.INTEGRATE_USER_DATA:
            return ExecodeParameterCollator._execode_user_integrate(action, xparams)

        return xparams

    @staticmethod
    def _check_missing_keys(action: Execode, xparams: dict):
        required_keys = ExecodeRequiredKeys.get_required_keys(action)

        missing_keys = required_keys.difference(xparams)
        if missing_keys:
            raise ExecodeCollationError(action, missing_keys, ExecodeCollationFailedReason.MISSING_KEY)

    @staticmethod
    def _execode_ar_add(action: Execode, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if isinstance(xparams[k], str) and len(xparams[k]) == 0:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.EMPTY_CONTENT)

        try:
            xparams[k] = Platform.cast(xparams[k])
        except KeyError as ex:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISSING_KEY, ex) from ex
        except Exception as ex:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISC, ex) from ex

        return xparams

    @staticmethod
    def _execode_conn_channel(xparams: dict) -> dict:
        return xparams

    @staticmethod
    def _execode_user_integrate(action: Execode, xparams: dict) -> dict:
        k = param.Execode.USER_OID

        try:
            xparams[k] = ObjectId(xparams[k])
        except InvalidId as ex:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.OBJECT_ID_INVALID, ex) from ex
        except KeyError as ex:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISSING_KEY, ex) from ex
        except Exception as ex:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISC, ex) from ex

        return xparams


class ExecodeRequiredKeys:
    """Class to get the required keys of the Execode action."""

    @staticmethod
    def get_required_keys(execode_type: Execode) -> Set[str]:
        """
        Get a set of required keys.

        :param execode_type: type of the Execode action
        :return: set of required keys
        """
        ret = set()

        if execode_type == Execode.AR_ADD:
            ret.add(param.AutoReply.CHANNEL_TOKEN)
            ret.add(param.AutoReply.PLATFORM)
        elif execode_type == Execode.REGISTER_CHANNEL:
            ret.add(param.Execode.CHANNEL_TOKEN)
            ret.add(param.Execode.PLATFORM)
        elif execode_type == Execode.INTEGRATE_USER_DATA:
            ret.add(param.Execode.USER_OID)

        return ret
