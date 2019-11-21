from typing import Optional

from bson import ObjectId

from extutils.checker import param_type_ensure
from flags import AutoReplyContentType
from models import AutoReplyContentModel, OID_KEY
from mongodb.factory.results import GetOutcome, AutoReplyContentAddResult, AutoReplyContentGetResult
from mongodb.utils import case_insensitive_collation

from ._base import BaseCollection
from ._mixin import CacheMixin

DB_NAME = "ar"


class AutoReplyContentManager(CacheMixin, BaseCollection):
    database_name = DB_NAME
    collection_name = "ctnt"
    model_class = AutoReplyContentModel

    cache_name = f"{DB_NAME}.{collection_name}"

    def __init__(self):
        super().__init__()
        self.create_index([(AutoReplyContentModel.Content.key, 1), (AutoReplyContentModel.ContentType.key, 1)],
                          name="Auto Reply Content Identity", unique=True)

    def add_content(self, content: str, type_: AutoReplyContentType) -> AutoReplyContentAddResult:
        entry, outcome, ex = self.insert_one_data(Content=content, ContentType=type_)

        self.set_cache(entry)

        return AutoReplyContentAddResult(outcome, entry, ex)

    def _get_content_(self, content: str, type_: AutoReplyContentType, case_insensitive: bool = False):
        q = self.empty_query()
        ret = self.get_cache(
            (q[AutoReplyContentModel.Content.key] == content) & (q[AutoReplyContentModel.ContentType.key] == type_),
            parse_cls=AutoReplyContentModel
        )

        if ret:
            return ret

        ret = self.find_one_casted(
            {AutoReplyContentModel.Content.key: content, AutoReplyContentModel.ContentType.key: type_},
            parse_cls=AutoReplyContentModel, collation=case_insensitive_collation if case_insensitive else None)

        if ret:
            self.set_cache(ret)

        return ret

    @param_type_ensure
    def get_content(
            self, content: str, type_: AutoReplyContentType = None, add_on_not_found=True, case_insensitive=True) \
            -> AutoReplyContentGetResult:
        if not content:
            return AutoReplyContentGetResult(GetOutcome.X_NO_CONTENT, None)

        if not type_:
            type_ = AutoReplyContentType.determine(content)

        ret_entry = self._get_content_(content, type_, case_insensitive)
        add_result = None

        entry_none = ret_entry is None

        if entry_none and add_on_not_found:
            add_result = self.add_content(content, type_)

            if add_result.outcome.is_inserted:
                ret_entry = self._get_content_(content, type_, case_insensitive)
                outcome = GetOutcome.O_ADDED
            else:
                outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT
        elif entry_none:
            outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT
        else:
            outcome = GetOutcome.O_CACHE_DB

        return AutoReplyContentGetResult(outcome, ret_entry, on_add_result=add_result)

    @param_type_ensure
    def get_content_by_id(self, oid: ObjectId) -> Optional[AutoReplyContentModel]:
        q = self.empty_query()
        ret = self.get_cache(q[OID_KEY] == oid, parse_cls=AutoReplyContentModel)

        if ret:
            return ret

        ret = self.find_one_casted({OID_KEY: oid}, parse_cls=AutoReplyContentModel)

        if ret:
            self.set_cache(ret)

        return ret


_inst = AutoReplyContentManager()
