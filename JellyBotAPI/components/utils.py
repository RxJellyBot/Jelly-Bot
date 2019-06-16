from JellyBotAPI import keys
from mongodb.factory import RootUserManager


def get_root_oid(request):
    exists = keys.USER_TOKEN in request.COOKIES
    root_u_result = None

    if exists:
        root_u_result = RootUserManager.get_root_data_api_token(request.COOKIES[keys.USER_TOKEN])
        if not root_u_result.success:
            del request.COOKIES[keys.USER_TOKEN]
            return None

    return root_u_result.model.id.value if exists else None
