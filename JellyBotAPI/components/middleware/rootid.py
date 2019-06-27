from django.utils.deprecation import MiddlewareMixin

from JellyBotAPI.keys import Session, Cookies
from JellyBotAPI.api.static import param
from mongodb.factory import RootUserManager


class RootUserIDInsertMiddleware(MiddlewareMixin):
    """
    Store the root user id to session if the http method is either POST or GET.

    Note:
        Must be used after using the `django.contrib.sessions.middleware.SessionMiddleware` because
        it store the root user ID into `Session`.
    """
    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        qd = None

        if request.method == "GET":
            qd = request.GET
        elif request.method == "POST":
            qd = request.POST

        if qd is not None:
            user_token = qd.get(param.Common.USER_TOKEN)
            platform = qd.get(param.Common.PLATFORM)

            if user_token is not None and platform is not None:
                rt_result = RootUserManager.get_root_data_onplat(platform, user_token)
                if rt_result.success:
                    request.session[Session.USER_ROOT_ID] = str(rt_result.model.id)
                    return

            api_token = request.COOKIES.get(Cookies.USER_TOKEN) or qd.get(param.Common.API_TOKEN)

            if api_token is not None:
                rt_result = RootUserManager.get_root_data_api_token(api_token)
                if rt_result.success:
                    request.session[Session.USER_ROOT_ID] = str(rt_result.model.id)
                    return
                else:
                    if Cookies.USER_TOKEN in request.COOKIES:
                        del request.COOKIES[Cookies.USER_TOKEN]
