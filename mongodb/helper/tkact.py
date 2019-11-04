from flags import Platform, TokenActionCollationFailedReason, TokenActionCompletionOutcome, TokenAction
from JellyBot.api.static import param
from models import AutoReplyModuleTokenActionModel, TokenActionModel
from mongodb.exceptions import NoCompleteActionError, TokenActionCollationError
from mongodb.factory import ChannelManager, AutoReplyManager, ProfileManager
from mongodb.helper import UserIdentityIntegrationHelper


__all__ = ["TokenActionCompletor", "TokenActionParameterCollator", "TokenActionRequiredKeys"]


class TokenActionCompletor:
    # noinspection PyArgumentList
    @staticmethod
    def complete_action(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        action = action_model.action_type
        xparams = TokenActionParameterCollator.collate_parameters(TokenAction(action), xparams)

        # TEST: Test token actions
        if action == TokenAction.AR_ADD:
            return TokenActionCompletor._token_ar_add_(action_model, xparams)
        elif action == TokenAction.REGISTER_CHANNEL:
            return TokenActionCompletor._token_register_channel_(action_model, xparams)
        elif action == TokenAction.INTEGRATE_USER_IDENTITY:
            return TokenActionCompletor._token_integrate_identity_(action_model, xparams)
        else:
            raise NoCompleteActionError(action)

    @staticmethod
    def _token_ar_add_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        cnl = ChannelManager.register(xparams[param.AutoReply.PLATFORM], xparams[param.AutoReply.CHANNEL_TOKEN])
        if not cnl.success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_CHANNEL

        try:
            conn = AutoReplyModuleTokenActionModel(**action_model.data, from_db=True).to_actual_model(
                cnl.model.id, action_model.creator_oid)
        except Exception:
            return TokenActionCompletionOutcome.X_MODEL_CONSTRUCTION

        if not AutoReplyManager.add_conn_by_model(conn).success:
            return TokenActionCompletionOutcome.X_AR_REGISTER_MODULE

        return TokenActionCompletionOutcome.O_OK

    @staticmethod
    def _token_register_channel_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        try:
            channel_data = ChannelManager.register(
                xparams[param.TokenAction.PLATFORM], xparams[param.TokenAction.CHANNEL_TOKEN])
        except Exception:
            return TokenActionCompletionOutcome.X_IDT_CHANNEL_ERROR

        if channel_data:
            try:
                ProfileManager.register_new_default(channel_data.model.id, action_model.creator_oid)
            except Exception:
                return TokenActionCompletionOutcome.X_IDT_REGISTER_DEFAULT_PROFILE
        else:
            return TokenActionCompletionOutcome.X_IDT_CHANNEL_NOT_FOUND

        return TokenActionCompletionOutcome.O_OK

    @staticmethod
    def _token_integrate_identity_(action_model: TokenActionModel, xparams: dict) -> TokenActionCompletionOutcome:
        try:
            # `xparams` is casted from QueryDict, so get the value using [0]
            success = UserIdentityIntegrationHelper.integrate(
                action_model.creator_oid, xparams.get(param.TokenAction.USER_OID)[0])
        except Exception:
            return TokenActionCompletionOutcome.X_IDT_INTEGRATION_ERROR

        if not success:
            return TokenActionCompletionOutcome.X_IDT_INTEGRATION_FAILED

        return TokenActionCompletionOutcome.O_OK


class TokenActionParameterCollator:
    @staticmethod
    def collate_parameters(action: TokenAction, xparams: dict) -> dict:
        if action == TokenAction.AR_ADD:
            return TokenActionParameterCollator._token_ar_add_(action, xparams)
        elif action == TokenAction.REGISTER_CHANNEL:
            return TokenActionParameterCollator._token_conn_channel_(xparams)
        else:
            return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _token_ar_add_(action: TokenAction, xparams: dict) -> dict:
        k = param.AutoReply.PLATFORM
        if xparams.get(k) is None or len(xparams[k][0]) == 0:
            raise TokenActionCollationError(action, k, TokenActionCollationFailedReason.EMPTY_CONTENT)
        else:
            try:
                xparams[k] = Platform(int(xparams[k][0]))
            except Exception as e:
                raise TokenActionCollationError(action, k, TokenActionCollationFailedReason.MISC, e)

        k = param.AutoReply.CHANNEL_TOKEN
        xparams[k] = xparams[k][0]

        return xparams

    # noinspection PyArgumentList
    @staticmethod
    def _token_conn_channel_(xparams: dict) -> dict:
        return {k: v[0] if isinstance(v, list) else v for k, v in xparams.items()}


class TokenActionRequiredKeys:
    @staticmethod
    def get_required_keys(token_action: TokenAction) -> set:
        st = {param.TokenAction.TOKEN}

        if token_action == TokenAction.AR_ADD:
            st.add(param.AutoReply.CHANNEL_TOKEN)
            st.add(param.AutoReply.PLATFORM)
        elif token_action == TokenAction.REGISTER_CHANNEL:
            st.add(param.TokenAction.CHANNEL_TOKEN)
            st.add(param.TokenAction.PLATFORM)
        elif token_action == TokenAction.INTEGRATE_USER_IDENTITY:
            st.add(param.TokenAction.USER_OID)

        return st