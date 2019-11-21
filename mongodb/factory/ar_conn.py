from datetime import timezone, timedelta
from typing import Tuple, Optional, List

import math
import pymongo
from bson import ObjectId
from datetime import datetime

from JellyBot.systemconfig import AutoReply, Database, DataQuery
from extutils.emailutils import MailSender
from extutils.checker import param_type_ensure
from extutils.color import ColorFactory
from flags import PermissionCategory, AutoReplyContentType
from models import AutoReplyModuleModel, AutoReplyModuleTagModel, AutoReplyTagPopularityDataModel, OID_KEY, \
    AutoReplyContentModel
from mongodb.factory.results import (
    WriteOutcome, GetOutcome,
    AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
)
from mongodb.utils import CursorWithCount, case_insensitive_collation
from mongodb.factory import ProfileManager, AutoReplyContentManager

from ._base import BaseCollection
from ._mixin import CacheMixin

DB_NAME = "ar"


class AutoReplyModuleManager(CacheMixin, BaseCollection):
    database_name = DB_NAME
    collection_name = "conn"
    model_class = AutoReplyModuleModel

    cache_name = f"{database_name}.{collection_name}"

    def __init__(self):
        super().__init__()
        self.create_index(
            [(AutoReplyModuleModel.KeywordOid.key, 1),
             (AutoReplyModuleModel.ResponseOids.key, 1),
             (AutoReplyModuleModel.ChannelId.key, 1)],
            name="Auto Reply Module Identity", unique=True)

    @staticmethod
    def has_access_to_pinned(channel_oid: ObjectId, user_oid: ObjectId):
        perms = ProfileManager.get_permissions(ProfileManager.get_user_profiles(channel_oid, user_oid))
        return PermissionCategory.AR_ACCESS_PINNED_MODULE in perms

    def add_conn_complete(
            self,
            kw_oid: ObjectId, rep_oids: Tuple[ObjectId], creator_oid: ObjectId, channel_oid: ObjectId,
            pinned: bool, private: bool, tag_ids: List[ObjectId], cooldown_sec: int) \
            -> AutoReplyModuleAddResult:
        access_to_pinned = AutoReplyModuleManager.has_access_to_pinned(channel_oid, creator_oid)

        # Terminate if someone without permission wants to create a pinned model
        if pinned and not access_to_pinned:
            return AutoReplyModuleAddResult(WriteOutcome.X_INSUFFICIENT_PERMISSION, None, None)

        # Terminate if someone cannot access pinned module but attempt to overwrite the existing one
        if not access_to_pinned and self.count_documents(
                {AutoReplyModuleModel.KeywordOid.key: kw_oid, AutoReplyModuleModel.Pinned.key: True}) > 0:
            return AutoReplyModuleAddResult(WriteOutcome.X_PINNED_CONTENT_EXISTED, None, None)

        model, outcome, ex = \
            self.insert_one_data(
                KeywordOid=kw_oid, ResponseOids=rep_oids, CreatorOid=creator_oid, Pinned=pinned,
                Private=private, CooldownSec=cooldown_sec, TagIds=tag_ids, ChannelId=channel_oid
            )

        # Set other module with the same keyword to be inactive
        filter_ = {
            AutoReplyModuleModel.Id.key: {"$ne": model.id},
            AutoReplyModuleModel.KeywordOid.key: kw_oid,
            AutoReplyModuleModel.ChannelId.key: channel_oid,
            AutoReplyModuleModel.Active.key: True
        }

        self.update_many(
            filter_,
            {"$set": {f"{AutoReplyModuleModel.Active.key}": False}})

        return AutoReplyModuleAddResult(outcome, model, ex)

    def add_conn_by_model(self, model: AutoReplyModuleModel) -> AutoReplyModuleAddResult:
        model.clear_oid()
        outcome, ex = self.insert_one_model(model)

        return AutoReplyModuleAddResult(outcome, model, ex)

    def module_mark_inactive(self, kw_oid: ObjectId, channel_oid: ObjectId, remover_oid: ObjectId) -> WriteOutcome:
        access_to_pinned = AutoReplyModuleManager.has_access_to_pinned(channel_oid, remover_oid)

        filter_ = {AutoReplyModuleModel.KeywordOid.key: kw_oid, AutoReplyModuleModel.ChannelId.key: channel_oid}

        if not access_to_pinned:
            filter_[AutoReplyModuleModel.Pinned.key] = False

        ret = self.update_one_outcome(
            filter_,
            {"$set": {
                AutoReplyModuleModel.Active.key: False,
                AutoReplyModuleModel.RemovedAt.key: datetime.now(tz=timezone.utc),
                AutoReplyModuleModel.RemoverOid.key: remover_oid
            }}
        )

        if ret == WriteOutcome.X_NOT_FOUND:
            # If the `Pinned` property becomes True then something found,
            # then it must because of the insufficient permission. Otherwise, it's really not found
            filter_[AutoReplyModuleModel.Pinned.key] = True
            if self.count_documents(filter_) > 0:
                return WriteOutcome.X_INSUFFICIENT_PERMISSION

        return ret

    @param_type_ensure
    def get_conn(self, keyword_oid: ObjectId, channel_oid: ObjectId) -> \
            Optional[AutoReplyModuleModel]:
        ret: Optional[AutoReplyModuleModel]

        q = self.empty_query()
        ret = self.get_cache(
            (q[AutoReplyModuleModel.KeywordOid.key] == keyword_oid) &
            (q[AutoReplyModuleModel.ChannelId.key] == channel_oid) &
            (q[AutoReplyModuleModel.Active.key]),
            parse_cls=AutoReplyModuleModel
        )

        if not ret:
            ret = self.find_one_casted(
                {AutoReplyModuleModel.KeywordOid.key: keyword_oid,
                 AutoReplyModuleModel.ChannelId.key: channel_oid,
                 AutoReplyModuleModel.Active.key: True}, parse_cls=AutoReplyModuleModel)

        if ret:
            now = datetime.now(tz=timezone.utc)
            if now - ret.last_used > timedelta(seconds=ret.cooldown_sec):
                self.update_one_async(
                    {AutoReplyModuleModel.Id.key: ret.id},
                    {"$set": {AutoReplyModuleModel.LastUsed.key: now},
                     "$inc": {AutoReplyModuleModel.CalledCount.key: 1}})
                return ret

        return None

    def get_conn_list(
            self, channel_oid: ObjectId, keyword_oids: List[ObjectId] = None, active_only: bool = True) \
            -> CursorWithCount:
        filter_ = {
            AutoReplyModuleModel.ChannelId.key: channel_oid
        }

        if keyword_oids:
            filter_[AutoReplyModuleModel.KeywordOid.key] = {"$in": keyword_oids}

        if active_only:
            filter_[AutoReplyModuleModel.Active.key] = True

        return self.find_cursor_with_count(filter_, parse_cls=AutoReplyModuleModel)


class AutoReplyModuleTagManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "tag"
    model_class = AutoReplyModuleTagModel

    def __init__(self):
        super().__init__()
        self.create_index(AutoReplyModuleTagModel.Name.key, name="Auto Reply Tag Identity", unique=True)

    def get_insert(self, name, color=ColorFactory.BLACK) -> AutoReplyModuleTagGetResult:
        ex = None
        tag_data = self.find_one_casted(
            {AutoReplyModuleTagModel.Name.key: name},
            parse_cls=AutoReplyModuleTagModel,
            collation=case_insensitive_collation)

        if tag_data:
            outcome = GetOutcome.O_CACHE_DB
        else:
            model, outcome, ex = \
                self.insert_one_data(Name=name, Color=color)

            if outcome.is_success:
                tag_data = model
                outcome = GetOutcome.O_ADDED
            else:
                outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT

        return AutoReplyModuleTagGetResult(outcome, tag_data, ex)

    def search_tags(self, tag_keyword: str) -> CursorWithCount:
        """
        Accepts a keyword to search. Case-insensitive.

        :param tag_keyword: Can be regex.
        """
        return self.find_cursor_with_count(
            {AutoReplyModuleTagModel.Name.key: {"$regex": tag_keyword, "$options": "i"}},
            sort=[(OID_KEY, pymongo.DESCENDING)],
            parse_cls=AutoReplyModuleTagModel)

    def get_tag_data(self, tag_oid: ObjectId) -> Optional[AutoReplyModuleTagModel]:
        return self.find_one_casted({OID_KEY: tag_oid}, parse_cls=AutoReplyModuleTagModel)


class AutoReplyManager:
    def __init__(self):
        self._mod = AutoReplyModuleManager()
        self._tag = AutoReplyModuleTagManager()

    def _get_tags_pop_score_(self, filter_word: str = None, count: int = DataQuery.TagPopularitySearchCount) \
            -> CursorWithCount:
        # Time Past Weighting: https://www.desmos.com/calculator/db92kdecxa
        # Appearance Weighting: https://www.desmos.com/calculator/a2uv5pqqku

        pipeline = []
        filter_ = {
            AutoReplyModuleModel.TagIds.key: {"$in": [tag_data.id for tag_data in self._tag.search_tags(filter_word)]}
        }

        if filter_word:
            pipeline.append({"$match": filter_})

        pipeline.append({"$unwind": "$" + AutoReplyModuleModel.TagIds.key})
        pipeline.append({"$group": {
            OID_KEY: "$" + AutoReplyModuleModel.TagIds.key,
            AutoReplyTagPopularityDataModel.WeightedAvgTimeDiff.key: {
                "$avg": {
                    "$divide": [
                        Database.PopularityConfig.TimeCoeffA,
                        {"$add": [
                            1,
                            {"$pow": [
                                math.e,
                                {"$multiply": [
                                    Database.PopularityConfig.TimeCoeffB,
                                    {"$subtract": [
                                        {"$divide": [
                                            {"$subtract": [
                                                {"$toDate": ObjectId.from_datetime(datetime.utcnow())},
                                                {"$toDate": "$" + AutoReplyTagPopularityDataModel.Id.key}
                                            ]},
                                            3600000
                                        ]},
                                        Database.PopularityConfig.TimeDiffIntersectHr
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]
                }
            },
            AutoReplyTagPopularityDataModel.Appearances.key: {"$sum": 1}
        }})
        pipeline.append({"$addFields": {
            AutoReplyTagPopularityDataModel.WeightedAppearances.key: {
                "$multiply": [
                    Database.PopularityConfig.AppearanceCoeffA,
                    {"$pow": [
                        "$" + AutoReplyTagPopularityDataModel.Appearances.key,
                        Database.PopularityConfig.AppearanceFunctionCoeff
                    ]}
                ]
            }
        }})
        pipeline.append({"$addFields": {
            AutoReplyTagPopularityDataModel.Score.key: {
                "$subtract": [
                    {"$multiply": [
                        Database.PopularityConfig.AppearanceEquivalentWHr,
                        "$" + AutoReplyTagPopularityDataModel.WeightedAppearances.key
                    ]},
                    "$" + AutoReplyTagPopularityDataModel.WeightedAvgTimeDiff.key
                ]
            }
        }})
        pipeline.append({"$sort": {
            AutoReplyTagPopularityDataModel.Score.key: pymongo.DESCENDING
        }})
        pipeline.append({"$limit": count})

        # Get the count of the result
        count_doc = min(count, self._mod.count_documents(filter_ if filter_word else {}))

        return CursorWithCount(self._mod.aggregate(pipeline), count_doc, parse_cls=AutoReplyTagPopularityDataModel)

    def add_conn_by_model(self, model: AutoReplyModuleModel) -> AutoReplyModuleAddResult:
        return self._mod.add_conn_by_model(model)

    def add_conn_complete(
            self, kw_oid: ObjectId, rep_oids: Tuple[ObjectId], creator_oid: ObjectId, channel_oid: ObjectId,
            pinned: bool, private: bool, tag_ids: List[ObjectId], cooldown_sec: int) \
            -> AutoReplyModuleAddResult:
        return self._mod.add_conn_complete(kw_oid, rep_oids, creator_oid, channel_oid, pinned, private, tag_ids,
                                           cooldown_sec)

    def del_conn(self, kw_oid: ObjectId, channel_oid: ObjectId, remover_oid: ObjectId) -> WriteOutcome:
        return self._mod.module_mark_inactive(kw_oid, channel_oid, remover_oid)

    def get_responses(
            self, keyword: str, keyword_type: AutoReplyContentType,
            channel_oid: ObjectId, case_insensitive: bool = True) -> List[Tuple[AutoReplyContentModel, bool]]:
        """
        :return: Empty list (length of 0) if no corresponding response.
                [(<RESPONSE_MODEL>, <BYPASS_MULTILINE>), (<RESPONSE_MODEL>, <BYPASS_MULTILINE>)...]
        """
        import time

        _start_ = time.time()

        ctnt_rst = AutoReplyContentManager.get_content(keyword, keyword_type, False, case_insensitive)
        mod = None
        resp_ctnt = []
        resp_id_miss = []

        if ctnt_rst.success:
            mod = self._mod.get_conn(ctnt_rst.model.id, channel_oid)

        if mod:
            resp_ids = mod.response_oids

            for resp_id in resp_ids:
                ctnt_mdl = AutoReplyContentManager.get_content_by_id(resp_id)
                if ctnt_mdl:
                    resp_ctnt.append((ctnt_mdl, mod.cooldown_sec > AutoReply.BypassMultilineCDThresholdSeconds))
                else:
                    resp_id_miss.append(resp_id)

        if resp_id_miss and ctnt_rst.success:
            content = f"""Malformed data detected.
            <hr>
            <h4>Parameters</h4><br>
            Keyword: {keyword} / Type: {keyword_type} / Case Insensitive: {case_insensitive}<br>
            <h4>Variables</h4><br>
            Get content result (keyword): {ctnt_rst}<br>
            Keyword connection model: {mod}<br>
            Contents to response: {mod}<br>
            Contents missing (id): {resp_id_miss}
            """
            MailSender.send_email_async(content, subject="Lossy data in auto reply database")

        return resp_ctnt

    def get_popularity_scores(self, search_keyword: str = None, count: int = DataQuery.TagPopularitySearchCount) \
            -> List[str]:
        """
        Get the :class:`list` of popular tag names sorted by the popularity score.
        """
        ret = []

        for score_model in self._get_tags_pop_score_(search_keyword, count):
            tag_data = self._tag.get_tag_data(score_model.id)
            if tag_data:
                ret.append(tag_data.name)

        return ret

    def tag_get_insert(self, name, color=ColorFactory.BLACK) -> AutoReplyModuleTagGetResult:
        return self._tag.get_insert(name, color)

    def get_conn_list(self, channel_oid: ObjectId, keyword_oids: List[ObjectId] = None, active_only: bool = True) \
            -> CursorWithCount:
        return self._mod.get_conn_list(channel_oid, keyword_oids, active_only)


_inst = AutoReplyManager()
