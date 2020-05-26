from datetime import datetime
from typing import Optional, Any

from bson import ObjectId

from JellyBot.systemconfig import Database
from flags import ExtraContentType
from models import ExtraContentModel, OID_KEY
from mongodb.factory.results import RecordExtraContentResult, WriteOutcome
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

    def record_extra_message(self, content: list, title: str = None, channel_oid: ObjectId = None):
        """
        :param content: [(<REASON>, <MESSAGE_CONTENT>), (<REASON>, <MESSAGE_CONTENT>)...]
        :param title: Title of the extra message.
        :param channel_oid: channel oid of this extra message
        """
        content = cast_iterable(content, str)

        return self.record_content(ExtraContentType.EXTRA_MESSAGE, content, title, channel_oid)

    def record_content(
            self, type_: ExtraContentType, content: Any, title: str = None, channel_oid: ObjectId = None) \
            -> RecordExtraContentResult:
        if not title:
            title = ExtraContentManager.DefaultTitle

        if not content:
            return RecordExtraContentResult(WriteOutcome.X_NOT_EXECUTED)

        model, outcome, ex = self.insert_one_data(
            Type=type_, Title=title, Content=content, Timestamp=datetime.utcnow(), ChannelOid=channel_oid)

        return RecordExtraContentResult(outcome, ex, model)

    @arg_type_ensure
    def get_content(self, content_id: ObjectId) -> Optional[ExtraContentModel]:
        return self.find_one_casted({OID_KEY: content_id}, parse_cls=ExtraContentModel)


_inst = ExtraContentManager()
