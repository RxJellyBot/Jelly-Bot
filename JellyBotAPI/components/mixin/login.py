from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View

from JellyBotAPI import keys
from mongodb.factory import MixedUserManager


class LoginRequiredMixin(UserPassesTestMixin, View):
    def test_func(self):
        exists = keys.USER_TOKEN in self.request.COOKIES

        if exists and not MixedUserManager.is_api_user_exists(self.request.COOKIES[keys.USER_TOKEN]):
            del self.request.COOKIES[keys.USER_TOKEN]
            return False

        return exists
