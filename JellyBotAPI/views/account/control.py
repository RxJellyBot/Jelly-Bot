from django.shortcuts import redirect
from django.utils import timezone
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import gettext as _

from JellyBotAPI import keys
from JellyBotAPI.components.mixin import LoginRequiredMixin
from JellyBotAPI.components.utils import get_root_oid, get_x_post_keys
from JellyBotAPI.views import render_template, simple_str_response
from extutils.locales import locales, now_utc_aware
from mongodb.factory import RootUserManager


class AccountLogoutView(View):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        response = redirect("page.home")
        response.delete_cookie(keys.Cookies.USER_TOKEN)

        return response


class AccountSettingsPageView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        update_result = RootUserManager.update_config(get_root_oid(request), **get_x_post_keys(request.POST))

        if update_result.success:
            return simple_str_response(
                request,
                f"success/{timezone.localtime(now_utc_aware()):%m-%d %H:%M:%S (%Z)} - " +
                _(f"Account settings updated."))
        else:
            return simple_str_response(
                request,
                f"danger/{timezone.localtime(now_utc_aware()):%m-%d %H:%M:%S (%Z)} - " +
                _("Account settings failed to update."))

    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        config = RootUserManager.get_config_root_oid(get_root_oid(request))

        return render_template(
            self.request, _("Account Settings"), "account/settings.html",
            {"locale_list": sorted(locales, key=lambda item: item.description),
             "current_config": config})
