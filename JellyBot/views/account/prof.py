from typing import Set

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.color import ColorFactory
from JellyBot.views import render_template
from JellyBot.components.mixin import PermissionRequiredMixin
from JellyBot.utils import get_post_keys, get_root_oid
from flags import PermissionCategoryDefault, PermissionCategory
from mongodb.factory import ProfileManager
from mongodb.helper import IdentitySearcher


class ProfileCreateView(PermissionRequiredMixin, TemplateResponseMixin, View):
    @staticmethod
    def required_permission() -> Set[PermissionCategory]:
        return {PermissionCategory.PRF_CONTROL_SELF}

    # noinspection PyUnusedLocal,PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        channel_data = self.get_channel_data(*args, **kwargs)
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


# noinspection PyUnusedLocal
class ProfileAttachView(PermissionRequiredMixin, TemplateResponseMixin, View):
    @staticmethod
    def required_permission() -> Set[PermissionCategory]:
        return {PermissionCategory.PRF_CONTROL_SELF}

    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        channel_data = self.get_channel_data(*args, **kwargs)
        channel_oid = channel_data.model.id

        attach_member = ProfileManager.can_attach_profile_member(
            ProfileManager.get_permissions(
                ProfileManager.get_user_profiles(channel_oid, root_oid)))

        member_list = {}
        if attach_member:
            member_list = IdentitySearcher.get_batch_user_name(
                [mdl.user_oid for mdl in ProfileManager.get_channel_members(channel_oid, True)], channel_data.model)
            member_list = sorted(member_list.items(), key=lambda item: item[1])

        return render_template(
            self.request, _("Attach Profile"), "account/channel/prof/attach.html",
            {
                "channel_oid": channel_oid,
                "attachable_profiles": ProfileManager.get_attachable_profiles(
                    root_oid, channel_data.model.get_oid()),
                "member_list": member_list
            }, nav_param=kwargs)
