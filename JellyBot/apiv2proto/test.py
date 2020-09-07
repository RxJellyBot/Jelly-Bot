"""Implementation of the API v2 prototype."""
import json

from django.http import JsonResponse
from django.views import View
from graphene import ObjectType, String, Schema

from extutils.serializer import JellyBotSerializer
from JellyBot.components.relay import CsrfExemptRelay


class Query(ObjectType):
    """GraphQL query entry point."""

    text = String(default_value="default_value", name=String(default_value="default_name"))

    @staticmethod
    def resolve_text(_, __, name):
        """Resolve parameter ``text``."""
        return f"Fuck you {name}!"


# noinspection PyTypeChecker
schema = Schema(query=Query)


class ApiV2PrototypeView(CsrfExemptRelay, View):
    """
    View for API v2 prototype.

    TODO: Validate that the content-type is either ``application/json`` or ``application/graphql``.

    CSRF Exempt is needed as query sent via Dart will always have the content type of ``application/json``.
    """

    @staticmethod
    def _handle_graphql(request):
        query_obj = json.loads(request.body)

        query_str = query_obj["query"]
        query_opname = query_obj.get("operationName")
        query_vars = query_obj.get("variables")

        print(query_str)
        print(query_opname)
        print(query_vars)

        result = schema.execute(query_str, operation_name=query_opname, variables=query_vars)

        return JsonResponse(result.to_dict(), encoder=JellyBotSerializer)

    def get(self, request):
        """
        Execute the value of ``query`` in the request body.

        ``Content-type`` is assumed to be ``application/json``.
        """
        return self._handle_graphql(request)

    def post(self, request):
        """
        Execute the value of ``query`` in the request body.

        ``Content-type`` is assumed to be ``application/json``.
        """
        return self._handle_graphql(request)
