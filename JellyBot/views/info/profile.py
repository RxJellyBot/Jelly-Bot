from bson import ObjectId

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateResponseMixin

from extutils import safe_cast
from flags import PermissionCategory, WebsiteError
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.helper import IdentitySearcher
from JellyBot.views import render_template, WebsiteErrorView
from JellyBot.utils import get_root_oid
from JellyBot.components.mixin import LoginRequiredMixin


class ProfileInfoView(LoginRequiredMixin, TemplateResponseMixin, View):
    def get(self, request, **kwargs):
        profile_oid_str = kwargs.get("profile_oid", "")
        profile_oid = safe_cast(profile_oid_str, ObjectId)

        profile_data = ProfileManager.get_profile(profile_oid)

        if not profile_data:
            return WebsiteErrorView.website_error(
                request, WebsiteError.PROFILE_NOT_FOUND, {"profile_oid": profile_oid})

        channel_model = ChannelManager.get_channel_oid(profile_data.channel_oid)
        names = IdentitySearcher.get_batch_user_name(ProfileManager.get_profile_user_oids(profile_oid),
                                                     channel_model, on_not_found=None)

        # noinspection PyTypeChecker
        return render_template(
            self.request, _("Profile Info - {}").format(profile_data.name), "info/profile.html", {
                "profile_data": profile_data,
                "perm_cats": list(PermissionCategory),
                "names": filter(lambda n: n is not None, names.values())
            }, nav_param=kwargs)
