from typing import Optional
from collections import OrderedDict

from django.apps import apps
from django.conf import settings
from bson import ObjectId

from flags import Platform
from mongodb.factory import RootUserManager
from JellyBot.keys import Session, ParamDictPrefix
from JellyBot.api.static.param import Common


def get_root_oid(request) -> Optional[ObjectId]:
    oid_str = request.session.get(Session.USER_ROOT_ID)
    if oid_str:
        return ObjectId(oid_str)

    u_token = request.GET.get(Common.USER_TOKEN)
    if u_token:
        platform = Platform.cast(request.GET.get(Common.PLATFORM)) or Platform.UNKNOWN
        result = RootUserManager.get_root_data_onplat(platform, u_token, auto_register=False)

        if result.success:
            return result.model.id

    api_token = request.GET.get(Common.API_TOKEN)
    if api_token:
        result = RootUserManager.get_root_data_api_token(api_token)

        if result.success:
            return result.model.id

    return None


def get_post_keys(qd):
    return {k.replace(ParamDictPrefix.PostKey, ""): v for k, v in qd.items()
            if k.startswith(ParamDictPrefix.PostKey)}


# Obtained and modified from https://stackoverflow.com/a/57897422
def load_server():
    apps.app_configs = OrderedDict()
    apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
    apps.clear_cache()
    apps.populate(settings.INSTALLED_APPS)
