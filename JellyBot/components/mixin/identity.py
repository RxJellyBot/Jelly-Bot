from typing import Set

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View

from JellyBot import keys
from JellyBot.utils import get_root_oid, get_channel_data
from JellyBot.views import WebsiteErrorView
from flags import ProfilePermission, WebsiteError
from mongodb.factory import ProfileManager


class LoginRequiredMixin(UserPassesTestMixin, View):
    def test_func(self):
        return get_root_oid(self.request) is not None and keys.Cookies.USER_TOKEN in self.request.COOKIES


class ChannelOidRequiredMixin(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._channel_data = None

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get_channel_data(self, *args, **kwargs):
        return get_channel_data(kwargs)

    # noinspection PyUnusedLocal
    def _get_channel_data_(self, *args, **kwargs):
        if not self._channel_data:
            self._channel_data = self.get_channel_data(*args, **kwargs)
        return self._channel_data

    def dispatch(self, request, *args, **kwargs):
        if not self.get_channel_data(*args, **kwargs).ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND,
                {"channel_oid": self.get_channel_data(*args, **kwargs).oid_org}, nav_param=kwargs)

        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(ChannelOidRequiredMixin, LoginRequiredMixin, View):
    @staticmethod
    def required_permission() -> Set[ProfilePermission]:
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)

        pass_ = ProfileManager.get_user_permissions(self.get_channel_data(*args, **kwargs).model.id, root_oid)\
            .issuperset(self.required_permission())

        if not pass_:
            return WebsiteErrorView.website_error(
                request, WebsiteError.INSUFFICIENT_PERMISSION,
                {"channel_oid": self.get_channel_data(*args, **kwargs).oid_org,
                 "required_permission": self.required_permission()}, nav_param=kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)
