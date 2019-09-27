from typing import Optional
from collections import OrderedDict

from django.apps import apps
from django.conf import settings
from bson import ObjectId

from JellyBot.keys import Session, ParamDictPrefix


def get_root_oid(request) -> Optional[ObjectId]:
    oid_str = request.session.get(Session.USER_ROOT_ID)

    return None if oid_str is None else ObjectId(oid_str)


def get_post_keys(qd):
    return {k.replace(ParamDictPrefix.PostKey, ""): v for k, v in qd.items()
            if k.startswith(ParamDictPrefix.PostKey)}


# Obtained and modified from https://stackoverflow.com/a/57897422
def load_server():
    apps.app_configs = OrderedDict()
    apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
    apps.clear_cache()
    apps.populate(settings.INSTALLED_APPS)
