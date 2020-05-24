from typing import Optional
from collections import OrderedDict, namedtuple

from django.apps import apps
from django.conf import settings
from bson import ObjectId

from extutils import safe_cast
from flags import Platform
from mongodb.factory import RootUserManager, ChannelManager, ProfileManager
from JellyBot.keys import Session, ParamDictPrefix
from JellyBot.api.static.param import Common


def get_root_oid(request) -> Optional[ObjectId]:
    oid_str = request.session.get(Session.USER_ROOT_ID)
    if oid_str:
        return ObjectId(oid_str)

    u_token = request.GET.get(Common.USER_TOKEN)
    if u_token:
        platform = Platform.cast(request.GET.get(Common.PLATFORM)) or Platform.UNKNOWN
        # OPTIMIZE: skip the steps of getting the API / OnPlat model (unnecessary)
        result = RootUserManager.get_root_data_onplat(platform, u_token, auto_register=False)

        if result.success:
            return result.model.id

    api_token = request.GET.get(Common.API_TOKEN)
    if api_token:
        # OPTIMIZE: skip the steps of getting the API / OnPlat model (unnecessary)
        result = RootUserManager.get_root_data_api_token(api_token)

        if result.success:
            return result.model.id

    return None


def get_post_keys(qd):
    return {k.replace(ParamDictPrefix.PostKey, ""): v for k, v in qd.items()
            if k.startswith(ParamDictPrefix.PostKey)}


ChannelDataGetResult = namedtuple("ChannelGetData", ["ok", "model", "oid_org"])


def get_channel_data(kwargs) -> ChannelDataGetResult:
    channel_oid_str = kwargs.get("channel_oid", "")
    channel_oid = safe_cast(channel_oid_str, ObjectId)

    model = ChannelManager.get_channel_oid(channel_oid)

    return ChannelDataGetResult(ok=model is not None, model=model, oid_org=channel_oid_str)


ProfileDataGetResult = namedtuple("ProfileGetData", ["ok", "model", "oid_org"])


def get_profile_data(kwargs) -> ProfileDataGetResult:
    profile_oid_str = kwargs.get("profile_oid", "")
    profile_oid = safe_cast(profile_oid_str, ObjectId)

    model = ProfileManager.get_profile(profile_oid)

    return ProfileDataGetResult(ok=model is not None, model=model, oid_org=profile_oid_str)


def get_limit(param_dict, max_: Optional[int] = None):
    limit = safe_cast(param_dict.get("limit"), int)
    if limit and max_:
        return min(limit, max_)
    else:
        return max_


# Obtained and modified from https://stackoverflow.com/a/57897422
def load_server():
    apps.app_configs = OrderedDict()
    apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
    apps.clear_cache()
    apps.populate(settings.INSTALLED_APPS)
