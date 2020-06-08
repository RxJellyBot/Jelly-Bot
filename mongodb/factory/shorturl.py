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

__all__ = ["ShortUrlDataManager"]

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
        service_url = os.environ.get("SERVICE_SHORT_URL")

        if not service_url:
            SYSTEM.logger.warning("Short URL service URL not found. Specify it as SERVICE_SHORT_URL in env var.")
            SYSTEM.logger.warning("Service availability not checked.")
            return False
        else:
            service_url = f"{service_url}/test"

        return _ShortUrlDataManager.is_valid_url(service_url)

    @staticmethod
    def is_valid_url(url) -> bool:
        return is_valid_url(url)

    def __init__(self):
        super().__init__()

        self.available = _ShortUrlDataManager.check_service()

        self.code_length = self._calc_code_length()

    def _calc_code_length(self) -> int:
        doc_count = self.count_documents({})

        if doc_count > 0:
            calc = math.ceil(math.log(self.count_documents({}), len(_ShortUrlDataManager.AVAILABLE_CHARACTERS)))
        else:
            calc = 0

        return max(calc, _ShortUrlDataManager.MIN_CODE_LENGTH)

    def generate_code(self):
        def generate():
            return "".join([random.choice(_ShortUrlDataManager.AVAILABLE_CHARACTERS) for _ in range(self.code_length)])

        code = generate()
        # Check if not existed in the database
        while self.count_documents({ShortUrlRecordModel.Code.key: code}) > 0:
            code = generate()

        return code

    @arg_type_ensure
    def create_record(self, target: str, creator_oid: ObjectId) -> UrlShortenResult:
        if not _ShortUrlDataManager.is_valid_url(target):
            return UrlShortenResult(WriteOutcome.X_INVALID_URL)

        model, outcome, ex = self.insert_one_data(Code=self.generate_code(), Target=target, CreatorOid=creator_oid)
        return UrlShortenResult(outcome, ex, model)

    @arg_type_ensure
    def get_target(self, code: str) -> Optional[str]:
        ret = self.get_record(code)

        if ret:
            return ret.target
        else:
            return None

    @arg_type_ensure
    def get_record(self, code: str) -> Optional[ShortUrlRecordModel]:
        return self.find_one_casted({ShortUrlRecordModel.Code.key: code}, parse_cls=ShortUrlRecordModel)

    @arg_type_ensure
    def get_user_record(self, creator_oid: ObjectId) -> ExtendedCursor[ShortUrlRecordModel]:
        filter_ = {ShortUrlRecordModel.CreatorOid.key: creator_oid}
        crs = ExtendedCursor(self.find(filter_), self.count_documents(filter_), parse_cls=ShortUrlRecordModel)
        return crs.sort([(ShortUrlRecordModel.Id.key, pymongo.ASCENDING)])

    @arg_type_ensure
    def update_target(self, creator_oid: ObjectId, code: str, new_target: str) -> bool:
        if not _ShortUrlDataManager.is_valid_url(new_target):
            return False

        return self.update_many_outcome(
            {ShortUrlRecordModel.CreatorOid.key: creator_oid, ShortUrlRecordModel.Code.key: code},
            {"$set": {ShortUrlRecordModel.Target.key: new_target}}
        ).is_success


ShortUrlDataManager = _ShortUrlDataManager()
