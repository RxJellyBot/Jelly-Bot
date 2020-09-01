"""Data manager for the Short URL service."""
import os
import math
import random
from typing import Optional

import pymongo
from bson import ObjectId

from extutils.url import is_valid_url
from extutils.logger import SYSTEM
from extutils.checker import arg_type_ensure
from models import ShortUrlRecordModel
from mongodb.factory.results import WriteOutcome, UrlShortenResult
from mongodb.utils import ExtendedCursor

from ._base import BaseCollection

__all__ = ("ShortUrlDataManager",)

DB_NAME = "surl"


class _ShortUrlDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "data"
    model_class = ShortUrlRecordModel

    MIN_CODE_LENGTH = 5
    AVAILABLE_CHARACTERS = \
        [chr(c) for c in range(ord('A'), ord('Z') + 1)] + [chr(c) for c in range(ord('a'), ord('z') + 1)]  # A-Z & a-z

    @staticmethod
    def check_service() -> bool:
        """
        Check if the service is up.

        This assumes that the service is running on the URL set as ``SERVICE_SHORT_URL`` in the environment variables.

        :return: if the service is up
        """
        service_url = os.environ.get("SERVICE_SHORT_URL")

        if not service_url:
            SYSTEM.logger.warning("Short URL service URL not found. Specify it as SERVICE_SHORT_URL in env var.")
            SYSTEM.logger.warning("Service availability not checked.")
            return False

        return is_valid_url(f"{service_url}/test")

    def __init__(self):
        super().__init__()

        self.available = _ShortUrlDataManager.check_service()

        self.code_length = self._calc_code_length()

    def _calc_code_length(self) -> int:
        doc_count = self.estimated_document_count()

        if doc_count > 0:
            calc = math.ceil(math.log(doc_count, len(_ShortUrlDataManager.AVAILABLE_CHARACTERS)))
        else:
            calc = 0

        return max(calc, _ShortUrlDataManager.MIN_CODE_LENGTH)

    def generate_code(self):
        """Generate a code for the short URL."""
        def generate():
            return "".join([random.choice(_ShortUrlDataManager.AVAILABLE_CHARACTERS) for _ in range(self.code_length)])

        code = generate()
        # Check if not existed in the database
        while self.count_documents({ShortUrlRecordModel.Code.key: code}) > 0:
            code = generate()

        return code

    @arg_type_ensure
    def create_record(self, target: str, creator_oid: ObjectId) -> UrlShortenResult:
        """
        Create a short URL record.

        :param target: target of the short URL record
        :param creator_oid: OID of the creator
        :return: short URL record creation result
        """
        if not is_valid_url(target):
            return UrlShortenResult(WriteOutcome.X_INVALID_URL)

        model, outcome, ex = self.insert_one_data(Code=self.generate_code(), Target=target, CreatorOid=creator_oid)
        return UrlShortenResult(outcome, ex, model)

    @arg_type_ensure
    def get_target(self, code: str) -> Optional[str]:
        """
        Get the target of the short URL by its code.

        :param code: code of the short URL
        :return: target of the short URL record
        """
        ret = self.get_record(code)

        if not ret:
            return None

        return ret.target

    @arg_type_ensure
    def get_record(self, code: str) -> Optional[ShortUrlRecordModel]:
        """
        Get the short URL record by its ``code``.

        Returns ``None`` if not found.

        :param code: code of the short URL record to get
        :return: `ShortUrlRecordModel` matching the condition if found, `None` otherwise
        """
        return self.find_one_casted({ShortUrlRecordModel.Code.key: code})

    @arg_type_ensure
    def get_user_record(self, creator_oid: ObjectId) -> ExtendedCursor[ShortUrlRecordModel]:
        """
        Get the short URLs created by ``creator_oid``.

        The returned result will be sorted by its creation timestamp (ASC).

        :param creator_oid: user who creates the returned short URLs
        :return: a cursor yielding the short URL data created by `creator_oid`
        """
        return self.find_cursor_with_count({ShortUrlRecordModel.CreatorOid.key: creator_oid},
                                           sort=[(ShortUrlRecordModel.Id.key, pymongo.ASCENDING)])

    @arg_type_ensure
    def update_target(self, creator_oid: ObjectId, code: str, new_target: str) -> bool:
        """
        Update the target of the short URL.

        Fail if ``new_target`` is not a valid URL.

        :param creator_oid: OID of the short URL creator
        :param code: code of the short URL to be updated
        :param new_target: new target for the short URL
        :return: if the update succeed
        """
        if not is_valid_url(new_target):
            return False

        return self.update_many_outcome(
            {ShortUrlRecordModel.CreatorOid.key: creator_oid, ShortUrlRecordModel.Code.key: code},
            {"$set": {ShortUrlRecordModel.Target.key: new_target}}
        ).is_success


ShortUrlDataManager = _ShortUrlDataManager()
