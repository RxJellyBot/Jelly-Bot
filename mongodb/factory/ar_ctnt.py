from flags import AutoReplyContentType

from models import AutoReplyContentModel
from mongodb.factory.results import InsertOutcome, GetOutcome, AutoReplyContentAddResult, AutoReplyContentGetResult

from ._base import BaseCollection


DB_NAME = "ar"


class AutoReplyContentManager(BaseCollection):
    def __init__(self):
        super().__init__(DB_NAME, "ctnt", AutoReplyContentModel.Content)
        self.create_index([(AutoReplyContentModel.Content, 1), (AutoReplyContentModel.ContentType, 1)],
                          name="Auto Reply Content Identity", unique=True)

    def add_content(self, content: str, type_: AutoReplyContentType) -> AutoReplyContentAddResult:
        entry, outcome, ex, insert_result = self.insert_one_data(AutoReplyContentModel,
                                                                 content=content.upper(), type=type_)

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(AutoReplyContentModel.Content, (entry.content.value, entry.type.value), entry)

        return AutoReplyContentAddResult(outcome, entry, ex)

    def _spec_get_cache_(self, content, type_):
        return self.get_cache(AutoReplyContentModel.Content, (content, type_),
                              acquire_args=({AutoReplyContentModel.Content: content,
                                             AutoReplyContentModel.ContentType: type_},),
                              parse_cls=AutoReplyContentModel, acquire_auto=True)

    def get_content(self, content: str, type_: AutoReplyContentType, add_on_not_found=True) \
            -> AutoReplyContentGetResult:
        if not isinstance(type_, AutoReplyContentType):
            type_ = AutoReplyContentType(type_)

        ret_entry = self._spec_get_cache_(content, type_)
        add_result = None

        if ret_entry is None and add_on_not_found:
            add_result = self.add_content(content, type_)

            if InsertOutcome.is_inserted(add_result.outcome):
                ret_entry = self._spec_get_cache_(content, type_)
                outcome = GetOutcome.SUCCESS_ADDED
            else:
                outcome = GetOutcome.FAILED_NOT_FOUND_ATTEMPTED_INSERT
        else:
            outcome = GetOutcome.SUCCESS_CACHE_DB

        return AutoReplyContentGetResult(outcome, ret_entry, on_add_result=add_result)


_inst = AutoReplyContentManager()
