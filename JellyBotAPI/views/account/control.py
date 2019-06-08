from django.shortcuts import redirect
from django.views import View

from JellyBotAPI import keys


class AccountLogoutView(View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        response = redirect("page.home")
        response.delete_cookie(keys.USER_TOKEN)

        return response
