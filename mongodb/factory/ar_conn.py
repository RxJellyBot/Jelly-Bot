from typing import Tuple
from bson import ObjectId

from extutils.color import ColorFactory
from flags import Platform
from models import AutoReplyModuleModel, AutoReplyModuleTagModel
from mongodb.factory.results import (
    InsertOutcome, GetOutcome,
    AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
)

from ._base import BaseCollection
# noinspection PyPep8Naming
from .channel import _inst as ChannelManager

DB_NAME = "ar"


class AutoReplyModuleManager(BaseCollection):
    # TODO: Auto Reply - Cache & Preload
    database_name = DB_NAME
    collection_name = "conn"
    model_class = AutoReplyModuleModel

    def __init__(self):
        super().__init__(AutoReplyModuleModel.KeywordOid.key)
        self.create_index(
            [(AutoReplyModuleModel.KeywordOid.key, 1), (AutoReplyModuleModel.ResponsesOids.key, 1)],
            name="Auto Reply Module Identity", unique=True)

    def add_conn(self, kw_oid: ObjectId, rep_oids: Tuple[ObjectId], creator_oid: ObjectId,
                 platform: Platform, channel_token: str, pinned: bool, private: bool, cooldown_sec: int) \
            -> AutoReplyModuleAddResult:
        # INCOMPLETE: Permission - Check if the user have the permission if pinned is true

        entry, ar_insert_outcome, ex, insert_result = \
            self.insert_one_data(
                AutoReplyModuleModel,
                KeywordOid=kw_oid, ResponsesOids=rep_oids, CreatorOid=creator_oid, Pinned=pinned,
                Private=private, CooldownSec=cooldown_sec
            )

        channel = ChannelManager.get_channel(platform, channel_token)

        def local_append_channel() -> InsertOutcome:
            return self.append_channel(kw_oid, rep_oids, channel.id)

        if InsertOutcome.data_found(ar_insert_outcome):
            if channel is None:
                reg_result = ChannelManager.register(platform, channel_token)
                if InsertOutcome.data_found(reg_result.outcome):
                    channel = reg_result.model
                    overall_outcome = local_append_channel()
                else:
                    overall_outcome = InsertOutcome.X_ON_REG_CHANNEL
            else:
                overall_outcome = local_append_channel()
        else:
            overall_outcome = InsertOutcome.X_INSERT_UNKNOWN

        return AutoReplyModuleAddResult(overall_outcome, ar_insert_outcome, entry, ex)

    def add_conn_by_model(self, model: AutoReplyModuleModel) -> AutoReplyModuleAddResult:
        model.clear_oid()
        outcome, ex = self.insert_one_model(model)

        return AutoReplyModuleAddResult(outcome, outcome, model, ex)

    def append_channel(self, kw_oid: ObjectId, rep_oids: Tuple[ObjectId], channel_oid: ObjectId) -> InsertOutcome:
        update_result = self.update_one(
            {AutoReplyModuleModel.KeywordOid.key: kw_oid, AutoReplyModuleModel.ResponsesOids.key: rep_oids},
            {"$addToSet": {AutoReplyModuleModel.ChannelIds.key: channel_oid}})

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                outcome = InsertOutcome.O_INSERTED
            else:
                outcome = InsertOutcome.O_DATA_EXISTS
        else:
            outcome = InsertOutcome.X_NOT_FOUND

        return outcome


class AutoReplyModuleTagManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "tag"
    model_class = AutoReplyModuleTagModel

    def __init__(self):
        super().__init__(AutoReplyModuleTagModel.Name.key)
        self.create_index(AutoReplyModuleTagModel.Name.key, name="Auto Reply Tag Identity", unique=True)

    def get_insert(self, name, color=ColorFactory.BLACK) -> AutoReplyModuleTagGetResult:
        ex = None
        tag_data = self.get_cache(
            AutoReplyModuleTagModel.Name.key, name, parse_cls=AutoReplyModuleTagModel, case_insensitive=True)

        if tag_data is None:
            model, outcome, ex, insert_result = \
                self.insert_one_data(AutoReplyModuleTagModel, Name=name, Color=color)

            if InsertOutcome.is_success(outcome):
                tag_data = self.set_cache(
                    AutoReplyModuleTagModel.Name.key, name, tag_data, parse_cls=AutoReplyModuleTagModel)
                outcome = GetOutcome.SUCCESS_ADDED
            else:
                outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT
        else:
            outcome = GetOutcome.SUCCESS_CACHE_DB

        return AutoReplyModuleTagGetResult(outcome, tag_data, ex)

    # FIXME: AutoReplyModuleTagManager
    #  Trace back `add_conn` to add the pipeline to passdown the tag and call `get_insert`
    #  UI Add tag window


_inst = AutoReplyModuleManager()
