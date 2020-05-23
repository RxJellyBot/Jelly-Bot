from flags import Platform, ExecodeCollationFailedReason, ExecodeCompletionOutcome, Execode
from JellyBot.api.static import param
from models import AutoReplyModuleExecodeModel, ExecodeEntryModel
from mongodb.exceptions import NoCompleteActionError, ExecodeCollationError
from mongodb.factory import ChannelManager, AutoReplyManager, ProfileManager
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
        cnl = ChannelManager.register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        if not cnl.success:
            return ExecodeCompletionOutcome.X_AR_REGISTER_CHANNEL

        try:
            conn = AutoReplyModuleExecodeModel(**action_model.data, from_db=True).to_actual_model(
                cnl.model.id, action_model.creator_oid)
        except Exception:
            return ExecodeCompletionOutcome.X_MODEL_CONSTRUCTION

        if not AutoReplyManager.add_conn_by_model(conn).success:
            return ExecodeCompletionOutcome.X_AR_REGISTER_MODULE

        return ExecodeCompletionOutcome.O_OK

    @staticmethod
    def _excde_register_channel(action_model: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        try:
            channel_data = ChannelManager.register(
                xparams[param.Execode.PLATFORM], xparams[param.Execode.CHANNEL_TOKEN])
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_ERROR

        if channel_data:
            try:
                ProfileManager.register_new_default(channel_data.model.id, action_model.creator_oid)
            except Exception:
                return ExecodeCompletionOutcome.X_IDT_REGISTER_DEFAULT_PROFILE
        else:
            return ExecodeCompletionOutcome.X_IDT_CHANNEL_NOT_FOUND

        return ExecodeCompletionOutcome.O_OK

    @staticmethod
    def _excde_user_data_integration(action_model: ExecodeEntryModel, xparams: dict) -> ExecodeCompletionOutcome:
        try:
            # `xparams` is casted from QueryDict, so get the value using [0]
            success = UserDataIntegrationHelper.integrate(
                action_model.creator_oid, xparams.get(param.Execode.USER_OID)[0])
        except Exception:
            return ExecodeCompletionOutcome.X_IDT_INTEGRATION_ERROR

        if not success:
            return ExecodeCompletionOutcome.X_IDT_INTEGRATION_FAILED

        return ExecodeCompletionOutcome.O_OK


class ExecodeParameterCollator:
    @staticmethod
    def collate_parameters(action: Execode, xparams: dict) -> dict:
        if action == Execode.AR_ADD:
            return ExecodeParameterCollator._execode_ar_add(action, xparams)
        elif action == Execode.REGISTER_CHANNEL:
            return ExecodeParameterCollator._execode_conn_channel(xparams)
        else:
            return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _execode_ar_add(action: Execode, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if xparams.get(k) is None or len(xparams[k][0]) == 0:
            raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.EMPTY_CONTENT)
        else:
            try:
                xparams[k] = Platform(int(xparams[k][0]))
            except Exception as e:
                raise ExecodeCollationError(action, k, ExecodeCollationFailedReason.MISC, e)

        k = param.AutoReply.CHANNEL_TOKEN
        xparams[k] = xparams[k][0]

        return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _execode_conn_channel(xparams: dict) -> dict:
        return {k: v[0] if isinstance(v, list) else v for k, v in xparams.items()}


class ExecodeRequiredKeys:
    @staticmethod
    def get_required_keys(execode_type: Execode) -> set:
        st = {param.Execode.EXECODE}

        if execode_type == Execode.AR_ADD:
            st.add(param.AutoReply.CHANNEL_TOKEN)
            st.add(param.AutoReply.PLATFORM)
        elif execode_type == Execode.REGISTER_CHANNEL:
            st.add(param.Execode.CHANNEL_TOKEN)
            st.add(param.Execode.PLATFORM)
        elif execode_type == Execode.INTEGRATE_USER_DATA:
            st.add(param.Execode.USER_OID)

        return st
