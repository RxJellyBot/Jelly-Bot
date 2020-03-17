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
from flags import PermissionCategory, WebsiteError
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.helper import ProfileHelper
from JellyBot.utils import get_root_oid
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components.mixin import LoginRequiredMixin


class InfoPageActionControl(Enum):
    UNKNOWN = -1

    DETACH = 0
    DELETE = 1

    @staticmethod
    def parse(s: str):
        if s == "detach":
            return InfoPageActionControl.DETACH
        if s == "delete":
            return InfoPageActionControl.DELETE
        else:
            return InfoPageActionControl.UNKNOWN

    @staticmethod
    def action_detach():
        pass


class ProfileInfoView(LoginRequiredMixin, TemplateResponseMixin, View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, **kwargs):
        profile_oid_str = kwargs.get("profile_oid", "")
        profile_oid = safe_cast(profile_oid_str, ObjectId)

        profile_data = ProfileManager.get_profile(profile_oid)

        if not profile_data:
            return WebsiteErrorView.website_error(
                request, WebsiteError.PROFILE_NOT_FOUND, {"profile_oid": profile_oid})

        channel_model = ChannelManager.get_channel_oid(profile_data.channel_oid)

        # noinspection PyTypeChecker
        return render_template(
            request, _("Profile Info - {}").format(profile_data.name), "info/profile.html", {
                "profile_data": profile_data,
                "profile_controls":
                    ProfileHelper.get_user_profile_controls(channel_model, profile_oid, get_root_oid(request)),
                "perm_cats": list(PermissionCategory),
            }, nav_param=kwargs)

    # noinspection PyMethodMayBeStatic
    def post(self, request, **kwargs):
        sender_oid = get_root_oid(request)

        profile_oid_str = kwargs.get("profile_oid", "")
        profile_oid = safe_cast(profile_oid_str, ObjectId)

        profile_data = ProfileManager.get_profile(profile_oid)

        if not profile_data:
            return HttpResponse(status=404)

        channel_model = ChannelManager.get_channel_oid(profile_data.channel_oid)

        # --- Get form data

        action = InfoPageActionControl.parse(request.POST.get("action"))
        uid = safe_cast(request.POST.get("uid"), ObjectId)

        if action == InfoPageActionControl.UNKNOWN or not uid:
            return HttpResponse(status=400)

        # --- Check permission

        target_self = sender_oid == uid

        permissions = ProfileManager.get_user_permissions(channel_model.id, sender_oid)

        # --- Execute corresponding action

        if action == InfoPageActionControl.DETACH:
            if target_self and PermissionCategory.PRF_CONTROL_SELF in permissions:
                pass
            elif PermissionCategory.PRF_CONTROL_MEMBER in permissions:
                pass
            else:
                return HttpResponse(status=403)

            detach_outcome = ProfileManager.detach_profile(uid, profile_oid)

            if detach_outcome.is_success:
                messages.info(request, _("Profile detached."))
            else:
                messages.warning(request, _("Failed to detach the profile. ({})").format(detach_outcome))

            return redirect(reverse("info.profile", kwargs={"profile_oid": profile_oid}))
        elif action == InfoPageActionControl.DELETE:
            pass
        else:
            return HttpResponse(status=501)
