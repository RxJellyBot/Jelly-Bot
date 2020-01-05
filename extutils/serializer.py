from bson import ObjectId
from django.core.serializers.json import DjangoJSONEncoder

from extutils.flags import is_flag_instance
from mongodb.factory.results import BaseResult
from models import Model


class JellyBotSerializer(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return o.to_json()
        elif isinstance(o, BaseResult):
            return o.serialize()
        elif isinstance(o, ObjectId):
            return repr(o)
        elif is_flag_instance(o):
            return int(o)
        elif isinstance(o, set):
            return list(o)
        else:
            return super().default(o)
