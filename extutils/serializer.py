from bson import ObjectId
from django.core.serializers.json import DjangoJSONEncoder

from extutils.flags import FlagCodeMixin
from mongodb.factory.results import BaseResult
from models import Model


class JellyBotAPISerializer(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return o.serialize()
        elif isinstance(o, BaseResult):
            return o.serialize()
        elif isinstance(o, ObjectId):
            return repr(o)
        elif isinstance(o, FlagCodeMixin):
            return int(o)
        else:
            return super().default(o)
