"""Customized JSON serializer for Django."""
from bson import ObjectId
from django.core.serializers.json import DjangoJSONEncoder

from extutils.flags import is_flag_instance
from mongodb.factory.results import BaseResult
from models import Model


class JellyBotSerializer(DjangoJSONEncoder):
    """Customized JSON serializer for Django."""

    def default(self, o):
        if isinstance(o, Model):
            return o.to_json()

        if isinstance(o, BaseResult):
            return o.serialize()

        if isinstance(o, ObjectId):
            return repr(o)

        if is_flag_instance(o):
            return int(o)

        if isinstance(o, set):
            return list(o)

        return super().default(o)
