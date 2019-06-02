from typing import Tuple
from bson import ObjectId

from flags import Platform
from models import AutoReplyConnectionModel, AutoReplyContentModel
from mongodb.factory.results import InsertOutcome, AutoReplyConnectionAddResult

from ._base import BaseCollection
from .channel import _inst as ChannelManager

DB_NAME = "ar"


class AutoReplyConnectionManager(BaseCollection):
    # DRAFT: (After Bridging) Cache (KW, CH - Flatten)

    def __init__(self):
        super().__init__(DB_NAME, "conn", AutoReplyContentModel.Content)
        self.create_index([(AutoReplyConnectionModel.KeywordID, 1), (AutoReplyConnectionModel.ResponsesIDs, 1)],
                          name="Auto Reply Connection Identity", unique=True)

    def add(self, kw_oid: ObjectId, rep_oids: Tuple[ObjectId], creator_oid: ObjectId,
            platform: Platform, channel_token: str, pinned: bool, private: bool, cooldown_sec: int) \
            -> AutoReplyConnectionAddResult:

        # TODO: Permission - Check if the user have the permission if pinned is true

        entry, ar_insert_outcome, ex, insert_result = \
            self.insert_one_data(
                AutoReplyConnectionModel,
                keyword_oid=kw_oid, responses_oids=rep_oids, creator_oid=creator_oid, pinned=pinned, disabled=False,
                private=private, cooldown_sec=cooldown_sec
            )

        channel = ChannelManager.get_channel(platform, channel_token)

        def append_channel() -> InsertOutcome:
            return self.append_channel(kw_oid, rep_oids, channel.id.value)

        if InsertOutcome.data_found(ar_insert_outcome):
            if channel is None:
                reg_result = ChannelManager.register(platform, channel_token)
                if InsertOutcome.data_found(reg_result.outcome):
                    channel = reg_result.model
                    overall_outcome = append_channel()
                else:
                    overall_outcome = InsertOutcome.FAILED_ON_REG_CHANNEL
            else:
                overall_outcome = append_channel()
        else:
            overall_outcome = InsertOutcome.FAILED_INSERT_UNKNOWN

        return AutoReplyConnectionAddResult(overall_outcome, ar_insert_outcome, entry, ex)

    def append_channel(self, kw_oid: ObjectId, rep_oids: Tuple[ObjectId], channel_oid: ObjectId) -> InsertOutcome:
        update_result = self.update_one(
            {AutoReplyConnectionModel.KeywordID: kw_oid, AutoReplyConnectionModel.ResponsesIDs: rep_oids},
            {"$addToSet": {AutoReplyConnectionModel.ChannelIDs: channel_oid}})

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                outcome = InsertOutcome.SUCCESS_INSERTED
            else:
                outcome = InsertOutcome.SUCCESS_DATA_EXISTS
        else:
            outcome = InsertOutcome.FAILED_NOT_FOUND

        return outcome


_inst = AutoReplyConnectionManager()
