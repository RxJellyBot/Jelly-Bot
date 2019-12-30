from bson import ObjectId

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils import safe_cast
from flags import PermissionCategory, WebsiteError
from mongodb.factory import ProfileManager
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.components.mixin import LoginRequiredMixin


class ProfileInfoView(LoginRequiredMixin, TemplateResponseMixin, View):
    def get(self, request, **kwargs):
        profile_oid_str = kwargs.get("profile_oid", "")
        profile_oid = safe_cast(profile_oid_str, ObjectId)

        profile_data = ProfileManager.get_profile(profile_oid)

        if not profile_data:
            return WebsiteErrorView.website_error(
                request, WebsiteError.PROFILE_NOT_FOUND, {"profile_oid": profile_oid})

        # noinspection PyTypeChecker
        return render_template(
            self.request, _("Profile Info - {}").format(profile_data.name), "info/profile.html", {
                "profile_data": profile_data,
                "perm_cats": list(PermissionCategory)
            }, nav_param=kwargs)
