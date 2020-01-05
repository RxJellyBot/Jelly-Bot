from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.color import ColorFactory
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components.mixin import LoginRequiredMixin
from JellyBot.utils import get_channel_data, get_post_keys, get_root_oid
from flags import WebsiteError, PermissionCategoryDefault, PermissionCategory
from mongodb.factory import ProfileManager


class ProfileCreateView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyUnusedLocal,PyTypeChecker
    def get(self, request, *args, **kwargs):
        channel_data = get_channel_data(kwargs)
        if not channel_data.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.CHANNEL_NOT_FOUND, {"channel_oid": channel_data.oid_org}, nav_param=kwargs)

        root_oid = get_root_oid(request)
        profiles = ProfileManager.get_user_profiles(channel_data.model.id, root_oid)
        max_perm_lv = ProfileManager.highest_permission_level(profiles)

        return render_template(
            self.request, _("Create Profile"), "account/channel/prof/create.html",
            {
                "channel_oid": channel_data.model.id,
                "max_perm_lv": max_perm_lv,
                "perm_cats_controllable": PermissionCategoryDefault.get_overridden_permissions(max_perm_lv),
                "perm_cats": list(PermissionCategory),
                "default_color": ColorFactory.BLACK.color_hex
            }, nav_param=kwargs)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        data = get_post_keys(request.POST)
        root_uid = get_root_oid(request)

        model = ProfileManager.register_new(root_uid, ProfileManager.process_profile_kwargs(data))

        if model:
            messages.info(request, _("Profile successfully created."))
        else:
            messages.warning(request, _("Failed to create the profile."))

        return redirect(reverse("account.profile.create", kwargs={"channel_oid": model.channel_oid}))
