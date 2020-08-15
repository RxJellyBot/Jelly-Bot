import os
from typing import Type

from bson import ObjectId

from JellyBot.api.static import result
from models import Model, ShortUrlRecordModel
from mongodb.factory.results import ModelResult, UrlShortenResult
from tests.base import TestOnModelResult

__all__ = ["TestUrlShortenResult"]


class TestUrlShortenResult(TestOnModelResult.TestClass):
    CREATOR_OID = ObjectId()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return UrlShortenResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ShortUrlRecordModel(
            Code="abcDEF", Target="https://google.com", CreatorOid=TestUrlShortenResult.CREATOR_OID)

    @classmethod
    def default_serialized(cls):
        d = super().default_serialized()
        d.update({result.Service.ShortUrl.SHORTENED_URL: f"{os.environ.get('SERVICE_SHORT_URL')}/abcDEF"})
        return d

    @classmethod
    def default_serialized_error(cls):
        d = super().default_serialized_error()
        d.update({result.Service.ShortUrl.SHORTENED_URL: None})
        return d
