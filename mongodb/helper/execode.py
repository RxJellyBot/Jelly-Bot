from bson import ObjectId
from bson.errors import InvalidId

from flags import Platform, ExecodeCollationFailedReason, ExecodeCompletionOutcome, Execode
from JellyBot.api.static import param
from models import ExecodeEntryModel, AutoReplyModuleModel
from mongodb.exceptions import NoCompleteActionError, ExecodeCollationError
from mongodb.factory import ChannelManager, AutoReplyManager, ProfileManager
from mongodb.factory.results import OperationOutcome
from mongodb.helper import UserDataIntegrationHelper

__all__ = ["ExecodeCompletor", "ExecodeParameterCollator", "ExecodeRequiredKeys"]


class ExecodeCompletor:
    # noinspection PyArgumentList
    @staticmethod
    def complete_execode(execode_entry: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        action = execode_entry.action_type
        xparams = ExecodeParameterCollator.collate_parameters(Execode(action), xparams)

        if action == Execode.AR_ADD:
            return ExecodeCompletor._excde_ar_add(execode_entry, xparams)
        elif action == Execode.REGISTER_CHANNEL:
            return ExecodeCompletor._excde_register_channel(execode_entry, xparams)
        elif action == Execode.INTEGRATE_USER_DATA:
            return ExecodeCompletor._excde_user_data_integration(execode_entry, xparams)
        else:
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
    def _excde_register_channel(action_model: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        try:
            reg_result = ChannelManager.ensure_register(
                xparams[param.Execode.PLATFORM], xparams[param.Execode.CHANNEL_TOKEN])
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_ERROR

        if not reg_result.success:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_ENSURE_FAILED

        try:
            result = ProfileManager.register_new_default(reg_result.model.id, action_model.creator_oid)

            if not result.success:
                return ExecodeCompletionOutcome.X_IDT_DEFAULT_PROFILE_FAILED
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_DEFAULT_PROFILE_ERROR

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
            elif result == OperationOutcome.X_DEST_DATA_NOT_FOUND:
                return ExecodeCompletionOutcome.X_IDT_TARGET_NOT_FOUND
            elif result == OperationOutcome.X_SAME_SRC_DEST:
                return ExecodeCompletionOutcome.X_IDT_SOURCE_EQ_TARGET
            else:
                return ExecodeCompletionOutcome.X_IDT_INTEGRATION_FAILED

        return ExecodeCompletionOutcome.O_OK


class ExecodeParameterCollator:
    @staticmethod
    def collate_parameters(action: Execode, xparams: dict) -> dict:
        if action == Execode.AR_ADD:
            return ExecodeParameterCollator._execode_ar_add(action, xparams)
        elif action == Execode.REGISTER_CHANNEL:
            return ExecodeParameterCollator._execode_conn_channel(xparams)
        elif action == Execode.INTEGRATE_USER_DATA:
            return ExecodeParameterCollator._execode_user_integrate(action, xparams)
        else:
            return xparams

    @staticmethod
    def _execode_ar_add(action: Execode, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if xparams.get(k) is None or len(xparams[k][0]) == 0:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.EMPTY_CONTENT)
        else:
            try:
                xparams[k] = Platform.cast(xparams[k][0])
            except KeyError as e:
                raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISSING_KEY, e)
            except Exception as e:
                raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISC, e)

        k = param.AutoReply.CHANNEL_TOKEN
        xparams[k] = xparams[k][0]

        return xparams

    @staticmethod
    def _execode_conn_channel(xparams: dict) -> dict:
        return {k: v[0] if isinstance(v, list) else v for k, v in xparams.items()}

    @staticmethod
    def _execode_user_integrate(action: Execode, xparams: dict) -> dict:
        k = param.Execode.USER_OID

        try:
            # This happens if `xparams` is casted to `QueryDict` which every value will stored as a `list`
            if isinstance(xparams[k], list):
                xparams[k] = xparams[k][0]

            xparams[k] = ObjectId(xparams[k])
        except InvalidId as e:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.OBJECT_ID_INVALID, e)
        except KeyError as e:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISSING_KEY, e)
        except Exception as e:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISC, e)

        return xparams


class ExecodeRequiredKeys:
    @staticmethod
    def get_required_keys(execode_type: Execode) -> set:
        st = set()

        if execode_type == Execode.AR_ADD:
            st.add(param.AutoReply.CHANNEL_TOKEN)
            st.add(param.AutoReply.PLATFORM)
        elif execode_type == Execode.REGISTER_CHANNEL:
            st.add(param.Execode.CHANNEL_TOKEN)
            st.add(param.Execode.PLATFORM)
        elif execode_type == Execode.INTEGRATE_USER_DATA:
            st.add(param.Execode.USER_OID)

        return st
