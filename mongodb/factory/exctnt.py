from typing import Optional, Any, List, Tuple

from bson import ObjectId

from JellyBot.systemconfig import Database
from flags import ExtraContentType
from models import ExtraContentModel, OID_KEY
from mongodb.factory.results import RecordExtraContentResult, WriteOutcome
from extutils.dt import now_utc_aware
from extutils.checker import arg_type_ensure
from extutils.utils import cast_iterable

from ._base import BaseCollection

DB_NAME = "ex"


class ExtraContentManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "content"
    model_class = ExtraContentModel

    DefaultTitle = "-"

    def __init__(self):
        super().__init__()
        self.create_index(ExtraContentModel.Timestamp.key,
                          expireAfterSeconds=Database.ExtraContentExpirySeconds, name="Timestamp")

    def record_extra_message(self, channel_oid: ObjectId, content: List[Tuple[str, str]], title: str = None) \
            -> RecordExtraContentResult:
        """
        Record an extra message.

        The 1st element of the content being passed in is
        the text reason of why the message is being recorded as an extra message.

        The 2nd element of the content being passed in is
        the message content.

        :param channel_oid: channel oid of this extra message
        :param content: message content to be recorded along with the reason
        :param title: title of the extra message
        """
        content = cast_iterable(content, str)

        return self.record_content(ExtraContentType.EXTRA_MESSAGE, channel_oid, content, title)

    def record_content(
            self, type_: ExtraContentType, channel_oid: ObjectId, content: Any, title: str = None) \
            -> RecordExtraContentResult:
        if not title:
            title = ExtraContentManager.DefaultTitle

        if not content:
            return RecordExtraContentResult(WriteOutcome.X_EMPTY_CONTENT)

        model, outcome, ex = self.insert_one_data(
            Type=type_, Title=title, Content=content, Timestamp=now_utc_aware(for_mongo=True), ChannelOid=channel_oid)

        return RecordExtraContentResult(outcome, ex, model)

    @arg_type_ensure
    def get_content(self, content_id: ObjectId) -> Optional[ExtraContentModel]:
        return self.find_one_casted({OID_KEY: content_id}, parse_cls=ExtraContentModel)


_inst = ExtraContentManager()
