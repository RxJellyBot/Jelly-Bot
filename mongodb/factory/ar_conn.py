from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Generator, Union

import math
import pymongo
from bson import ObjectId

from JellyBot.systemconfig import AutoReply, Database, DataQuery, Bot
from extutils.utils import enumerate_ranking
from extutils.checker import param_type_ensure
from extutils.color import ColorFactory
from extutils.dt import now_utc_aware
from flags import PermissionCategory, AutoReplyContentType
from models import AutoReplyModuleModel, AutoReplyModuleTagModel, AutoReplyTagPopularityDataModel, OID_KEY, \
    AutoReplyContentModel, UniqueKeywordCountResult
from models.field import DateTimeField
from models.utils import AutoReplyValidators
from mongodb.factory.results import (
    WriteOutcome, GetOutcome,
    AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
)
from mongodb.utils import (
    CursorWithCount, case_insensitive_collation,
    Query, MatchPair, UpdateOperation, Set, Increment, NotEqual
)
from mongodb.factory import ProfileManager

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
            [(AutoReplyModuleModel.KEY_KW_CONTENT, 1),
             (AutoReplyModuleModel.KEY_KW_TYPE, 1),
             (AutoReplyModuleModel.Responses.key, 1),
             (AutoReplyModuleModel.ChannelId.key, 1)],
            name="Auto Reply Module Identity", unique=True)

    @staticmethod
    def has_access_to_pinned(channel_oid: ObjectId, user_oid: ObjectId):
        perms = ProfileManager.get_permissions(ProfileManager.get_user_profiles(channel_oid, user_oid))
        return PermissionCategory.AR_ACCESS_PINNED_MODULE in perms

    @staticmethod
    def validate_content(
            keyword: str, kw_type: AutoReplyContentType, responses: List[AutoReplyContentModel], online_check) \
            -> WriteOutcome:
        if not AutoReplyValidators.is_valid_content(kw_type, keyword, online_check):
            return WriteOutcome.X_AR_INVALID_KEYWORD

        for response in responses:
            if not AutoReplyValidators.is_valid_content(response.content_type, response.content, online_check):
                return WriteOutcome.X_AR_INVALID_RESPONSE

        return WriteOutcome.O_MISC

    def _delete_recent_module_(self, keyword):
        """Delete modules which is created and marked inactive within `Bot.AutoReply.DeleteDataMins` minutes."""
        now = now_utc_aware()

        self.delete_many(
            {
                OID_KEY: {
                    "$lt": ObjectId.from_datetime(now),
                    "$gt": ObjectId.from_datetime(now - timedelta(minutes=Bot.AutoReply.DeleteDataMins))
                },
                AutoReplyModuleModel.KEY_KW_CONTENT: keyword,
                AutoReplyModuleModel.Active.key: False
            },
            collation=case_insensitive_collation if AutoReply.CaseInsensitive else None
        )

    def add_conn_complete(
            self,
            keyword: str, kw_type: AutoReplyContentType, responses: List[AutoReplyContentModel], creator_oid: ObjectId,
            channel_oid: ObjectId, pinned: bool, private: bool, tag_ids: List[ObjectId], cooldown_sec: int) \
            -> AutoReplyModuleAddResult:
        access_to_pinned = AutoReplyModuleManager.has_access_to_pinned(channel_oid, creator_oid)

        # Terminate if someone without permission wants to create a pinned model
        if pinned and not access_to_pinned:
            return AutoReplyModuleAddResult(WriteOutcome.X_INSUFFICIENT_PERMISSION, None, None)

        # Terminate if someone cannot access pinned module but attempt to overwrite the existing one
        if not access_to_pinned and self.count_documents(
                {AutoReplyModuleModel.KEY_KW_CONTENT: keyword,
                 AutoReplyModuleModel.KEY_KW_TYPE: kw_type,
                 AutoReplyModuleModel.Pinned.key: True}) > 0:
            return AutoReplyModuleAddResult(WriteOutcome.X_PINNED_CONTENT_EXISTED, None, None)

        validate_outcome = AutoReplyModuleManager.validate_content(keyword, kw_type, responses, online_check=True)

        if not validate_outcome.is_success:
            return AutoReplyModuleAddResult(validate_outcome, None, None)

        model, outcome, ex = \
            self.insert_one_data_cache(
                Keyword=AutoReplyContentModel(Content=keyword, ContentType=kw_type), Responses=responses,
                CreatorOid=creator_oid, Pinned=pinned, Private=private, CooldownSec=cooldown_sec, TagIds=tag_ids,
                ChannelId=channel_oid
            )

        if outcome.data_found:
            q_revive = Query(MatchPair(OID_KEY, model.id))
            op_revive = UpdateOperation(
                Set(
                    {
                        AutoReplyModuleModel.Active.key: True,
                        AutoReplyModuleModel.RemovedAt.key: DateTimeField.none_obj(),
                        AutoReplyModuleModel.RemoverOid.key: None
                    }
                )
            )

            outcome = self.update_cache_db_outcome(q_revive, op_revive)

        if outcome.is_success:
            # Set other module with the same keyword to be inactive
            q = Query(MatchPair(AutoReplyModuleModel.Id.key, NotEqual(model.id)),
                      MatchPair(AutoReplyModuleModel.KEY_KW_TYPE, kw_type),
                      MatchPair(AutoReplyModuleModel.KEY_KW_CONTENT, keyword),
                      MatchPair(AutoReplyModuleModel.ChannelId.key, channel_oid),
                      MatchPair(AutoReplyModuleModel.Active.key, True))

            self.update_cache_db_outcome(q, self._remove_update_ops_(creator_oid))
            self._delete_recent_module_(keyword)

        return AutoReplyModuleAddResult(outcome, model, ex)

    def add_conn_by_model(self, model: AutoReplyModuleModel, online_check=True) -> AutoReplyModuleAddResult:
        model.clear_oid()

        validate_outcome = AutoReplyModuleManager.validate_content(
            model.keyword.content, model.keyword.content_type, model.responses, online_check)

        if not validate_outcome.is_success:
            return AutoReplyModuleAddResult(validate_outcome, None, None)

        outcome, ex = self.insert_one_model_cache(model)

        if outcome.is_success:
            self._delete_recent_module_(model.keyword.content)

        return AutoReplyModuleAddResult(outcome, model, ex)

    @param_type_ensure
    def _remove_update_ops_(self, remover_oid: ObjectId) -> UpdateOperation:
        return UpdateOperation(
            Set(
                {
                    AutoReplyModuleModel.Active.key: False,
                    AutoReplyModuleModel.RemovedAt.key: now_utc_aware(),
                    AutoReplyModuleModel.RemoverOid.key: remover_oid
                }
            )
        )

    def module_mark_inactive(self, keyword: str, channel_oid: ObjectId, remover_oid: ObjectId) -> WriteOutcome:
        q = Query(MatchPair(AutoReplyModuleModel.KEY_KW_CONTENT, keyword),
                  MatchPair(AutoReplyModuleModel.ChannelId.key, channel_oid))

        if not AutoReplyModuleManager.has_access_to_pinned(channel_oid, remover_oid):
            q.add_element(MatchPair(AutoReplyModuleModel.Pinned.key, False))

        ret = self.update_cache_db_outcome(q, self._remove_update_ops_(remover_oid))

        if ret == WriteOutcome.X_NOT_FOUND:
            # If the `Pinned` property becomes True then something found,
            # then it must because of the insufficient permission. Otherwise, it's really not found
            q.add_element(MatchPair(AutoReplyModuleModel.Pinned.key, True))
            if self.count_documents(q.to_mongo()) > 0:
                return WriteOutcome.X_INSUFFICIENT_PERMISSION

        return ret

    @param_type_ensure
    def get_conn(self, keyword: str, keyword_type: AutoReplyContentType,
                 channel_oid: ObjectId, case_insensitive: bool = True) -> \
            Optional[AutoReplyModuleModel]:
        q = Query(MatchPair(AutoReplyModuleModel.KEY_KW_CONTENT, keyword),
                  MatchPair(AutoReplyModuleModel.KEY_KW_TYPE, keyword_type),
                  MatchPair(AutoReplyModuleModel.ChannelId.key, channel_oid),
                  MatchPair(AutoReplyModuleModel.Active.key, True))

        ret: Optional[AutoReplyModuleModel] = \
            self.get_cache_one(q,
                               parse_cls=AutoReplyModuleModel,
                               collation=case_insensitive_collation if case_insensitive else None)

        if ret:
            now = now_utc_aware()
            if now - ret.last_used > timedelta(seconds=ret.cooldown_sec):
                q_found = Query(MatchPair(AutoReplyModuleModel.Id.key, ret.id))
                u_query = UpdateOperation(
                    Set({AutoReplyModuleModel.LastUsed.key: now}),
                    Increment([AutoReplyModuleModel.CalledCount.key])
                )

                self.update_cache_db_async(q_found, u_query)
                return ret

        return None

    def get_conn_list(
            self, channel_oid: ObjectId, keyword: str = None, active_only: bool = True) \
            -> CursorWithCount:
        """Sort by used count (desc)."""
        filter_ = {
            AutoReplyModuleModel.ChannelId.key: channel_oid
        }

        if keyword:
            filter_[AutoReplyModuleModel.KEY_KW_CONTENT] = {"$regex": keyword, "$options": "i"}

        if active_only:
            filter_[AutoReplyModuleModel.Active.key] = True

        return self.find_cursor_with_count(
            filter_, parse_cls=AutoReplyModuleModel).sort([(AutoReplyModuleModel.CalledCount.key, pymongo.DESCENDING)])

    def get_module_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) -> CursorWithCount:
        ret = self.find_cursor_with_count(
            {AutoReplyModuleModel.ChannelId.key: channel_oid},
            parse_cls=AutoReplyModuleModel
        ).sort([(AutoReplyModuleModel.CalledCount.key, pymongo.DESCENDING)])

        if limit:
            ret = ret.limit(limit)

        return ret

    def get_unique_keyword_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> UniqueKeywordCountResult:
        pipeline = [
            {"$match": {AutoReplyModuleModel.ChannelId.key: channel_oid}},
            {"$group": {
                OID_KEY: {
                    UniqueKeywordCountResult.KEY_WORD: "$" + AutoReplyModuleModel.KEY_KW_CONTENT,
                    UniqueKeywordCountResult.KEY_WORD_TYPE: "$" + AutoReplyModuleModel.KEY_KW_TYPE
                },
                UniqueKeywordCountResult.KEY_COUNT_USAGE: {"$sum": "$" + AutoReplyModuleModel.CalledCount.key},
                UniqueKeywordCountResult.KEY_COUNT_MODULE: {"$sum": 1}
            }},
            {"$sort": {UniqueKeywordCountResult.KEY_COUNT_USAGE: pymongo.DESCENDING}}
        ]

        if limit:
            pipeline.append({"$limit": limit})

        return UniqueKeywordCountResult(self.aggregate(pipeline), limit)


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
            self, keyword: str, kw_type: AutoReplyContentType, responses: List[AutoReplyContentModel],
            creator_oid: ObjectId, channel_oid: ObjectId, pinned: bool, private: bool, tag_ids: List[ObjectId],
            cooldown_sec: int) \
            -> AutoReplyModuleAddResult:
        return self._mod.add_conn_complete(keyword, kw_type, responses, creator_oid, channel_oid, pinned, private,
                                           tag_ids, cooldown_sec)

    def del_conn(self, keyword: str, channel_oid: ObjectId, remover_oid: ObjectId) -> WriteOutcome:
        return self._mod.module_mark_inactive(keyword, channel_oid, remover_oid)

    def get_responses(
            self, keyword: str, keyword_type: AutoReplyContentType,
            channel_oid: ObjectId, case_insensitive: bool = True) -> List[Tuple[AutoReplyContentModel, bool]]:
        """
        :return: Empty list (length of 0) if no corresponding response.
                [(<RESPONSE_MODEL>, <BYPASS_MULTILINE>), (<RESPONSE_MODEL>, <BYPASS_MULTILINE>)...]
        """
        mod = self._mod.get_conn(keyword, keyword_type, channel_oid, case_insensitive=case_insensitive)
        resp_ctnt = []

        if mod:
            resp_ctnt = [(AutoReplyContentModel.cast_model(resp_mod),
                          mod.cooldown_sec > AutoReply.BypassMultilineCDThresholdSeconds)
                         for resp_mod in mod.responses]

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

    def get_conn_list(self, channel_oid: ObjectId, keyword: str = None, active_only: bool = True) \
            -> CursorWithCount:
        return self._mod.get_conn_list(channel_oid, keyword, active_only)

    def get_module_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> Generator[Tuple[Union[int, str], AutoReplyModuleModel], None, None]:
        return enumerate_ranking(self._mod.get_module_count_stats(channel_oid, limit),
                                 is_equal=lambda cur, prv: cur.called_count == prv.called_count)

    def get_unique_keyword_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> UniqueKeywordCountResult:
        return self._mod.get_unique_keyword_count_stats(channel_oid, limit)


_inst = AutoReplyManager()
