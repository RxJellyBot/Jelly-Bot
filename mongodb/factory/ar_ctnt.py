from typing import Optional

from bson import ObjectId

from extutils.checker import param_type_ensure
from flags import AutoReplyContentType
from models import AutoReplyContentModel, OID_KEY
from mongodb.factory.results import GetOutcome, AutoReplyContentAddResult, AutoReplyContentGetResult
from mongodb.utils import case_insensitive_collation, Query, MatchPair, StringContains, CursorWithCount

from ._base import BaseCollection
from ._mixin import CacheMixin

DB_NAME = "ar"


class AutoReplyContentManager(CacheMixin, BaseCollection):
    database_name = DB_NAME
    collection_name = "ctnt"
    model_class = AutoReplyContentModel

    cache_name = f"{database_name}.{collection_name}"

    def __init__(self):
        super().__init__()
        self.create_index([(AutoReplyContentModel.Content.key, 1), (AutoReplyContentModel.ContentType.key, 1)],
                          name="Auto Reply Content Identity", unique=True)

    def add_content(self, content: str, type_: AutoReplyContentType) -> AutoReplyContentAddResult:
        entry, outcome, ex = self.insert_one_data_cache(Content=content, ContentType=type_)

        return AutoReplyContentAddResult(outcome, entry, ex)

    def _get_content_(self, content: str, type_: AutoReplyContentType, case_insensitive: bool = False):
        q = Query(MatchPair(AutoReplyContentModel.Content.key, content),
                  MatchPair(AutoReplyContentModel.ContentType.key, type_))
        ret = self.get_cache_one(
            q, parse_cls=AutoReplyContentModel, collation=case_insensitive_collation if case_insensitive else None)

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

    def get_contents_by_word(self, keyword: str, case_insensitive: bool = True) -> CursorWithCount:
        q = Query(MatchPair(AutoReplyContentModel.Content.key, StringContains(keyword)))

        return self.find_cursor_with_count(
            q.to_mongo(),
            collation=case_insensitive_collation if case_insensitive else None,
            parse_cls=AutoReplyContentModel)

    @param_type_ensure
    def get_content_by_id(self, oid: ObjectId) -> Optional[AutoReplyContentModel]:
        return self.get_cache_one(Query(MatchPair(OID_KEY, oid)), parse_cls=AutoReplyContentModel)


_inst = AutoReplyContentManager()
