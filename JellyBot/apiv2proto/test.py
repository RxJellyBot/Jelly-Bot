"""Implementation of the API v2 prototype."""
import json

from django.http import JsonResponse
from django.views import View
from graphene import ObjectType, String, Schema

from extutils.serializer import JellyBotSerializer


class Query(ObjectType):
    """GraphQL query entry point."""

    text = String(default_value="default_value", name=String(default_value="default_name"))

    @staticmethod
    def resolve_text(_, __, name):
        """Resolve parameter ``text``."""
        return f"Fuck you {name}!"


# noinspection PyTypeChecker
schema = Schema(query=Query)


class ApiV2PrototypeView(View):
    """View for API v2 prototype."""

    def get(self, request):
        """
        Execute the value of ``query`` in the request body.

        ``Content-type`` must be ``application/json``.
        """
        query = json.loads(request.body)

        result = schema.execute(query["query"])

        return JsonResponse(result.to_dict(), encoder=JellyBotSerializer)
