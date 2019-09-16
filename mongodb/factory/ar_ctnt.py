from typing import Optional

from bson import ObjectId

from extutils.utils import is_empty_string
from extutils.checker import DecoParamCaster
from flags import AutoReplyContentType
from models import AutoReplyContentModel, OID_KEY
from mongodb.factory.results import InsertOutcome, GetOutcome, AutoReplyContentAddResult, AutoReplyContentGetResult

from ._base import BaseCollection

DB_NAME = "ar"


class AutoReplyContentManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "ctnt"
    model_class = AutoReplyContentModel

    def __init__(self):
        super().__init__(AutoReplyContentModel.Content.key)
        self.create_index([(AutoReplyContentModel.Content.key, 1), (AutoReplyContentModel.ContentType.key, 1)],
                          name="Auto Reply Content Identity", unique=True)

    def add_content(self, content: str, type_: AutoReplyContentType) -> AutoReplyContentAddResult:
        entry, outcome, ex, insert_result = self.insert_one_data(AutoReplyContentModel,
                                                                 Content=content, ContentType=type_)

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(AutoReplyContentModel.Content.key, (entry.content, entry.content_type), entry)

        return AutoReplyContentAddResult(outcome, entry, ex)

    def _spec_get_cache_(self, content: str, type_: AutoReplyContentType, case_insensitive: bool = False):
        return self.get_cache(AutoReplyContentModel.Content.key, (content, type_),
                              acquire_args=({AutoReplyContentModel.Content.key: content,
                                             AutoReplyContentModel.ContentType.key: type_},),
                              parse_cls=AutoReplyContentModel, case_insensitive=case_insensitive)

    @DecoParamCaster({2: AutoReplyContentType})
    def get_content(self, content: str, type_: AutoReplyContentType, add_on_not_found=True, case_insensitive=True) \
            -> AutoReplyContentGetResult:
        if is_empty_string(content):
            return AutoReplyContentGetResult(GetOutcome.X_NO_CONTENT, None)

        ret_entry = self._spec_get_cache_(content, type_, case_insensitive)
        add_result = None

        entry_none = ret_entry is None

        if entry_none and add_on_not_found:
            add_result = self.add_content(content, type_)

            if InsertOutcome.is_inserted(add_result.outcome):
                ret_entry = self._spec_get_cache_(content, type_, case_insensitive)
                outcome = GetOutcome.O_ADDED
            else:
                outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT
        elif entry_none:
            outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT
        else:
            outcome = GetOutcome.O_CACHE_DB

        return AutoReplyContentGetResult(outcome, ret_entry, on_add_result=add_result)

    @DecoParamCaster({1: ObjectId})
    def get_content_by_id(self, oid: ObjectId) -> Optional[AutoReplyContentModel]:
        return self.get_cache_condition(
            AutoReplyContentModel.Content.key, lambda x: x.id == oid,
            acquire_args=({OID_KEY: oid},), parse_cls=AutoReplyContentModel)


_inst = AutoReplyContentManager()
