from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View

from JellyBot import keys
from JellyBot.components import get_root_oid


class LoginRequiredMixin(UserPassesTestMixin, View):
    def test_func(self):
        return get_root_oid(self.request) is not None and keys.Cookies.USER_TOKEN in self.request.COOKIES
