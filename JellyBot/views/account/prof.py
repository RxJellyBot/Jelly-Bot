from typing import Set

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils.color import ColorFactory
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_post_keys, get_root_oid, get_profile_data
from JellyBot.components.mixin import PermissionRequiredMixin, LoginRequiredMixin, ChannelOidRequiredMixin
from flags import PermissionCategoryDefault, PermissionCategory, WebsiteError
from mongodb.factory import ProfileManager
from mongodb.helper import IdentitySearcher, ProfileHelper


class ProfileCreateView(PermissionRequiredMixin, TemplateResponseMixin, View):
    @staticmethod
    def required_permission() -> Set[PermissionCategory]:
        return {PermissionCategory.PRF_CED}

    # noinspection PyTypeChecker
    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        channel_data = self.get_channel_data(*args, **kwargs)
        profiles = ProfileManager.get_user_profiles(channel_data.model.id, root_oid)
        max_perm_lv = ProfileManager.get_highest_permission_level(profiles)

        return render_template(
            self.request, _("Create Profile"), "account/channel/prof/create.html",
            {
                "channel_oid": channel_data.model.id,
                "max_perm_lv": max_perm_lv,
                "perm_cats_controllable": PermissionCategoryDefault.get_overridden_permissions(max_perm_lv),
                "perm_cats": list(PermissionCategory),
                "value_color": ColorFactory.BLACK.color_hex
            }, nav_param=kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        data = get_post_keys(request.POST)
        root_uid = get_root_oid(request)

        model = ProfileManager.register_new(root_uid, ProfileManager.process_create_profile_kwargs(data))

        if model:
            messages.info(request, _("Profile successfully created."))
        else:
            messages.warning(request, _("Failed to create the profile."))

        return redirect(reverse("info.profile", kwargs={"profile_oid": model.id}))


class ProfileAttachView(PermissionRequiredMixin, TemplateResponseMixin, View):
    @staticmethod
    def required_permission() -> Set[PermissionCategory]:
        return {PermissionCategory.PRF_CONTROL_SELF}

    def get(self, request, *args, **kwargs):
        root_oid = get_root_oid(request)
        channel_data = self.get_channel_data(*args, **kwargs)
        channel_oid = channel_data.model.id

        attach_member = ProfileManager.can_control_profile_member(
            ProfileManager.get_user_permissions(channel_oid, root_oid))

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
                    channel_data.model.get_oid(), root_oid),
                "member_list": member_list
            }, nav_param=kwargs)


class ProfileEditView(PermissionRequiredMixin, TemplateResponseMixin, View):
    @staticmethod
    def required_permission() -> Set[PermissionCategory]:
        return {PermissionCategory.PRF_CED}

    def get(self, request, *args, **kwargs):
        profile_result = get_profile_data(kwargs)

        if not profile_result.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.PROFILE_NOT_FOUND, {"profile_oid": profile_result.oid_org})

        profile_model = profile_result.model

        return render_template(
            self.request, _("Edit Profile"), "account/channel/prof/edit.html",
            {
                "value_color": profile_model.color.color_hex,
                "value_name": profile_model.name
            }, nav_param=kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        profile_result = get_profile_data(kwargs)

        if not profile_result.ok:
            return HttpResponse(status=404)

        profile_oid = profile_result.model.id

        outcome = ProfileManager.update_profile(
            profile_result.model.id, ProfileManager.process_edit_profile_kwargs(get_post_keys(request.POST)))

        if outcome.is_success:
            messages.info(request, _("Profile successfully updated."))
            return redirect(reverse("info.profile", kwargs={"profile_oid": profile_oid}))
        else:
            channel_oid = profile_result.model.channel_oid

            messages.warning(request, _("Failed to update the profile."))
            return redirect(reverse("account.profile.edit",
                                    kwargs={"channel_oid": channel_oid, "profile_oid": profile_oid}))


class ProfileListView(LoginRequiredMixin, ChannelOidRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyTypeChecker
    def get(self, request, *args, **kwargs):
        channel_result = self.get_channel_data(*args, **kwargs)

        return render_template(
            self.request, _("List Profile"), "account/channel/prof/list.html",
            {
                "prof_entry": ProfileHelper.get_channel_profiles(channel_result.model.id),
                "perm_cats": list(PermissionCategory)
            }, nav_param=kwargs)
