from enum import Enum

from bson import ObjectId

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils import safe_cast
from flags import ProfilePermission, WebsiteError
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.helper import ProfileHelper
from JellyBot.utils import get_root_oid, get_profile_data
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components.mixin import LoginRequiredMixin


class InfoPageActionControl(Enum):
    UNKNOWN = -1

    DETACH = 0
    DELETE = 1

    def is_argument_valid(self, target_uid):
        if self == InfoPageActionControl.UNKNOWN:
            return False
        elif self == InfoPageActionControl.DETACH:
            return target_uid is not None
        elif self == InfoPageActionControl.DELETE:
            return True

        raise NotImplementedError()

    @staticmethod
    def parse(s: str):
        if s == "detach":
            return InfoPageActionControl.DETACH
        if s == "delete":
            return InfoPageActionControl.DELETE
        else:
            return InfoPageActionControl.UNKNOWN

    @staticmethod
    def action_detach(request, channel_oid, sender_oid, target_uid, permissions, profile_oid):
        target_self = sender_oid == target_uid

        # Permission Check
        if target_self and ProfilePermission.PRF_CONTROL_SELF in permissions:
            pass
        elif ProfilePermission.PRF_CONTROL_MEMBER in permissions:
            pass
        else:
            return HttpResponse(status=403)

        # Main Action
        detach_outcome = ProfileManager.detach_profile(channel_oid, profile_oid, target_uid)

        # Alert messages
        if detach_outcome.is_success:
            messages.info(request, _("Profile detached."))
        else:
            messages.warning(request, _("Failed to detach the profile. ({})").format(detach_outcome))

        return redirect(reverse("info.profile", kwargs={"profile_oid": profile_oid}))

    @staticmethod
    def action_delete(request, channel_model, profile_oid):
        # Terminate if the profile to be deleted is the default profile
        if channel_model.config.default_profile_oid == profile_oid:
            messages.warning(request, _("Attempted to delete the default profile which is not allowed."))
            return redirect(reverse("info.profile", kwargs={"profile_oid": profile_oid}))

        # Detach profile from all users and delete the profile from the database
        deleted = ProfileManager.delete_profile(channel_model.id, profile_oid)

        # Alert messages
        if deleted:
            messages.info(request, _("Profile deleted."))
            return redirect(reverse("account.channel.list"))
        else:
            messages.warning(request, _("Failed to delete the profile."))
            return redirect(reverse("info.profile", kwargs={"profile_oid": profile_oid}))


class ProfileInfoView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, **kwargs):
        profile_result = get_profile_data(kwargs)

        if not profile_result.ok:
            return WebsiteErrorView.website_error(
                request, WebsiteError.PROFILE_NOT_FOUND, {"profile_oid": profile_result.oid_org})

        root_oid = get_root_oid(request)
        profile_model = profile_result.model

        channel_model = ChannelManager.get_channel_oid(profile_model.channel_oid)
        permissions = ProfileManager.get_user_permissions(channel_model.id, root_oid)

        # noinspection PyTypeChecker
        return render_template(
            request, _("Profile Info - {}").format(profile_model.name), "info/profile.html", {
                "profile_data": profile_model,
                "profile_controls":
                    ProfileHelper.get_user_profile_controls(channel_model, profile_model.id, root_oid, permissions),
                "perm_cats": list(ProfilePermission),
                "is_default": profile_model.id == channel_model.config.default_profile_oid
            }, nav_param=kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request, **kwargs):
        sender_oid = get_root_oid(request)

        profile_result = get_profile_data(kwargs)

        if not profile_result.ok:
            return HttpResponse(status=404)

        channel_model = ChannelManager.get_channel_oid(profile_result.model.channel_oid)

        # --- Get form data

        action = InfoPageActionControl.parse(request.POST.get("action"))
        target_uid = safe_cast(request.POST.get("uid"), ObjectId)

        if not action.is_argument_valid(target_uid):
            return HttpResponse(status=400)

        # --- Check permission

        permissions = ProfileManager.get_user_permissions(channel_model.id, sender_oid)

        # --- Execute corresponding action

        profile_oid = profile_result.model.id

        if action == InfoPageActionControl.DETACH:
            return InfoPageActionControl.action_detach(
                request, channel_model.id, sender_oid, target_uid, permissions, profile_oid)
        elif action == InfoPageActionControl.DELETE:
            return InfoPageActionControl.action_delete(
                request, channel_model, profile_oid)
        else:
            return HttpResponse(status=501)
