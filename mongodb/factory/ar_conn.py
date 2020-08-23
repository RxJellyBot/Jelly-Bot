from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Generator, Union

import math
import pymongo
from bson import ObjectId

from JellyBot.systemconfig import AutoReply, Database, DataQuery, Bot
from extutils.utils import enumerate_ranking
from extutils.checker import arg_type_ensure
from extutils.color import ColorFactory
from extutils.dt import now_utc_aware
from flags import ProfilePermission, AutoReplyContentType
from mixin import ClearableMixin
from models import (
    AutoReplyModuleModel, AutoReplyModuleTagModel, AutoReplyTagPopularityScore, OID_KEY,
    AutoReplyContentModel, UniqueKeywordCountResult
)
from models.exceptions import ModelConstructionError, ModelKeyNotExistError
from models.utils import AutoReplyValidator
from mongodb.factory.results import (
    WriteOutcome, GetOutcome, UpdateOutcome,
    AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
)
from mongodb.utils import (
    ExtendedCursor, case_insensitive_collation
)
from mongodb.factory import ProfileManager

from ._base import BaseCollection

__all__ = ("AutoReplyManager", "AutoReplyModuleManager", "AutoReplyModuleTagManager",)

DB_NAME = "ar"


class _AutoReplyModuleManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "conn"
    model_class = AutoReplyModuleModel

    cache_name = f"{database_name}.{collection_name}"

    def build_indexes(self):
        # Using `_validate_content` to track the uniqueness of the modules instead of creating a index
        self.create_index(
            [(AutoReplyModuleModel.KEY_KW_CONTENT, 1),
             (AutoReplyModuleModel.KEY_KW_TYPE, 1),
             (AutoReplyModuleModel.ChannelOid.key, 1),
             (AutoReplyModuleModel.Active.key, 1)],
            name="Index to get module")

    @staticmethod
    def _has_access_to_pinned(channel_oid: ObjectId, user_oid: ObjectId):
        perms = ProfileManager.get_user_permissions(channel_oid, user_oid)
        return ProfilePermission.AR_ACCESS_PINNED_MODULE in perms

    def _validate_content(self, mdl: AutoReplyModuleModel, *, online_check=True) -> WriteOutcome:
        """
        Perform the following checks and return the corresponding result:

        - Validity of the keyword
            - ``WriteOutcome.X_AR_INVALID_KEYWORD`` if invalid
        - Validity of the responses
            - ``WriteOutcome.X_AR_INVALID_RESPONSE`` if invalid
        - Module duplicated
            - ``WriteOutcome.O_DATA_EXISTS`` if duplicated

        Returns ``WriteOutcome.O_MISC`` if the validation passed.

        :param mdl: model to be validated
        :return: validation result
        """
        # Check validity of keyword
        if not AutoReplyValidator.is_valid_content(
                mdl.keyword.content_type, mdl.keyword.content, online_check=online_check):
            return WriteOutcome.X_AR_INVALID_KEYWORD

        # Check validity of responses
        for response in mdl.responses:
            if not AutoReplyValidator.is_valid_content(
                    response.content_type, response.content, online_check=online_check):
                return WriteOutcome.X_AR_INVALID_RESPONSE

        # Check module duplication
        if self.count_documents(
                {
                    AutoReplyModuleModel.Keyword.key: mdl.keyword.to_json(),
                    AutoReplyModuleModel.Responses.key: mdl.responses,
                    AutoReplyModuleModel.ChannelOid.key: mdl.channel_oid
                },
                collation=case_insensitive_collation) > 0:
            return WriteOutcome.O_DATA_EXISTS

        return WriteOutcome.O_MISC

    def _delete_recent_module(self, keyword):
        """Delete modules which is created and marked inactive within `Bot.AutoReply.DeleteDataMins` minutes."""
        now = now_utc_aware()

        self.delete_many(
            {
                OID_KEY: {
                    "$gt": ObjectId.from_datetime(now - timedelta(minutes=Bot.AutoReply.DeleteDataMins))
                },
                AutoReplyModuleModel.KEY_KW_CONTENT: keyword,
                AutoReplyModuleModel.Active.key: False
            },
            collation=case_insensitive_collation if AutoReply.CaseInsensitive else None
        )

    @arg_type_ensure
    def _remove_update_ops(self, remover_oid: ObjectId):
        return {"$set": {
            AutoReplyModuleModel.Active.key: False,
            AutoReplyModuleModel.RemovedAt.key: now_utc_aware(),
            AutoReplyModuleModel.RemoverOid.key: remover_oid
        }}

    def _model_inherit_props(self, mdl: AutoReplyModuleModel):
        mdl_original = self.get_conn(
            mdl.keyword.content, mdl.keyword.content_type, mdl.channel_oid, update_count=False)

        if mdl_original:
            mdl.cooldown_sec = mdl_original.cooldown_sec
            mdl.tag_ids = mdl_original.tag_ids
            mdl.private = mdl_original.private

    def add_conn(self, *, online_check=True, **kwargs) -> AutoReplyModuleAddResult:
        """
        Add a auto-reply module to the database.

        If any :class:`ModelConstructionError` occurred during the model construction
            :class:`WriteOutcome.X_INVALID_MODEL` will be returned as the outcome

        If any :class:`ModelKeyNotExistError` occurred during the model construction
            :class:`WriteOutcome.X_MODEL_KEY_NOT_EXIST` will be returned as the outcome

        If any :class:`ModelKeyNotExistError` occurred during the model construction
            :class:`WriteOutcome.X_MODEL_KEY_NOT_EXIST` will be returned as the outcome

        If the model is marked as **PINNED**, but the creator does not have the corresponding permission
            :class:`WriteOutcome.X_INSUFFICIENT_PERMISSION` will be returned as the outcome

        If the creator does not have the corresponding permission
            :class:`WriteOutcome.X_PINNED_CONTENT_EXISTED` will be returned as the outcome

        If the content of the keyword is invalid
            :class:`WriteOutcome.X_AR_INVALID_KEYWORD` will be returned as the outcome

        If the content of any of the responses is invalid
            :class:`WriteOutcome.X_AR_INVALID_RESPONSE` will be returned as the outcome

        :param online_check: validate the content online
        :param kwargs: kwargs to construct a `AutoReplyModuleModel`
        :return: serializable result of the connection addition
        """
        # Create a model
        try:
            mdl = AutoReplyModuleModel(**kwargs)
        except ModelConstructionError as ex:
            return AutoReplyModuleAddResult(WriteOutcome.X_INVALID_MODEL, ex)
        except ModelKeyNotExistError as ex:
            return AutoReplyModuleAddResult(WriteOutcome.X_MODEL_KEY_NOT_EXIST, ex)

        # Pinned module creation permission check
        access_to_pinned = _AutoReplyModuleManager._has_access_to_pinned(mdl.channel_oid, mdl.creator_oid)

        if mdl.pinned and not access_to_pinned:
            return AutoReplyModuleAddResult(WriteOutcome.X_INSUFFICIENT_PERMISSION)

        # Terminate if someone cannot access pinned module but attempt to overwrite the existing one
        if not mdl.pinned and self.count_documents(
                {AutoReplyModuleModel.Keyword.key: mdl.keyword.to_json(),
                 AutoReplyModuleModel.Pinned.key: True}) > 0:
            return AutoReplyModuleAddResult(WriteOutcome.X_PINNED_CONTENT_EXISTED)

        validate_outcome = self._validate_content(mdl, online_check=online_check)

        if not validate_outcome.is_success:
            return AutoReplyModuleAddResult(validate_outcome)

        self._model_inherit_props(mdl)

        outcome, ex = self.insert_one_model(mdl)

        # Duplication was already checked when validating the content
        # However, the module ID is not acquired during check, so the module insertion still performed
        if outcome == WriteOutcome.O_DATA_EXISTS:
            # Re-enables the module if exactly same module found
            # Check unique indexes of what "same" means

            self.update_many(
                {AutoReplyModuleModel.Id.key: mdl.id},
                {"$set": {AutoReplyModuleModel.Active.key: True}})

        if outcome.is_success:
            # Set other module with the same keyword to be inactive

            self.update_many(
                {
                    AutoReplyModuleModel.Id.key: {"$ne": mdl.id},
                    AutoReplyModuleModel.Keyword.key: mdl.keyword.to_json(),
                    AutoReplyModuleModel.ChannelOid.key: mdl.channel_oid,
                    AutoReplyModuleModel.Active.key: True
                },
                self._remove_update_ops(mdl.creator_oid),
                collation=case_insensitive_collation
            )
            self._delete_recent_module(mdl.keyword.content)

        return AutoReplyModuleAddResult(outcome, ex, mdl)

    def module_mark_inactive(self, keyword: str, channel_oid: ObjectId, remover_oid: ObjectId) -> UpdateOutcome:
        q = {
            AutoReplyModuleModel.KEY_KW_CONTENT: keyword,
            AutoReplyModuleModel.ChannelOid.key: channel_oid,
            AutoReplyModuleModel.Active.key: True
        }

        if not _AutoReplyModuleManager._has_access_to_pinned(channel_oid, remover_oid):
            q[AutoReplyModuleModel.Pinned.key] = False

        ret = self.update_many_outcome(q, self._remove_update_ops(remover_oid), collation=case_insensitive_collation)

        if ret.is_success:
            self._delete_recent_module(keyword)
        elif ret == UpdateOutcome.X_NOT_FOUND:
            # If the `Pinned` property becomes True then something found,
            # then it must because of the insufficient permission. Otherwise, it's really not found
            q[AutoReplyModuleModel.Pinned.key] = True
            if self.count_documents(q) > 0:
                return UpdateOutcome.X_INSUFFICIENT_PERMISSION

        return ret

    @arg_type_ensure
    def get_conn(self, keyword: str, keyword_type: AutoReplyContentType, channel_oid: ObjectId, *,
                 update_async: bool = True, update_count: bool = True) -> \
            Optional[AutoReplyModuleModel]:
        """
        Get a auto reply module by providing the keyword, its type and the channel oid.

        Only returns the active module if exists.

        The called count of the returned module **includes** the current call.

        :param keyword: expected keyword of the module to get
        :param keyword_type: expected type of the keyword of the module to get
        :param channel_oid: expected affilitated channel
        :param update_count: if the called count should be updated
        :param update_async: if the info update should be performed asynchronously
        :return: an active auto reply module if exists
        """
        ret: Optional[AutoReplyModuleModel] = \
            self.find_one_casted(
                {
                    AutoReplyModuleModel.KEY_KW_CONTENT: keyword,
                    AutoReplyModuleModel.KEY_KW_TYPE: keyword_type,
                    AutoReplyModuleModel.ChannelOid.key: channel_oid,
                    AutoReplyModuleModel.Active.key: True
                },
                collation=case_insensitive_collation if AutoReply.CaseInsensitive else None)

        if not ret:
            return None

        now = now_utc_aware()
        if not ret.can_be_used(now):
            return None

        if update_count:
            q_found = {AutoReplyModuleModel.Id.key: ret.id}
            u_query = {
                "$set": {AutoReplyModuleModel.LastUsed.key: now},
                "$inc": {AutoReplyModuleModel.CalledCount.key: 1}
            }

            # Normally async is preferred to boost the speed, no async update for tests
            if update_async:
                self.update_one_async(q_found, u_query)
            else:
                self.update_one(q_found, u_query)

            ret.called_count += 1

        return ret

    def get_conn_list(self, channel_oid: ObjectId, keyword: Optional[str] = None, *, active_only: bool = True) \
            -> ExtendedCursor[AutoReplyModuleModel]:
        """
        Get the auto-reply module list in ``channel_oid`` with ``keyword``.

        ``keyword`` can be a part of the module keyword, but **NOT** the response.

        If ``keyword`` is not set or ``None``, all modules in ``channel_oid`` will be returned.

        Returned result will be sorted by module used count (DESC).

        :param channel_oid: channel of the module(s)
        :param keyword: keyword to filter the returning module(s)
        :param active_only: if to return active modules only
        :return: a cursor yielding the modules which match the given conditions
        """
        filter_ = {AutoReplyModuleModel.ChannelOid.key: channel_oid}

        if keyword:
            filter_[AutoReplyModuleModel.KEY_KW_CONTENT] = {"$regex": keyword, "$options": "i"}

        if active_only:
            filter_[AutoReplyModuleModel.Active.key] = True

        return self.find_cursor_with_count(filter_, sort=[(AutoReplyModuleModel.CalledCount.key, pymongo.DESCENDING)])

    def get_conn_list_oids(self, conn_oids: List[ObjectId]) -> ExtendedCursor[AutoReplyModuleModel]:
        """
        Get a list of auto-reply modules sorted by used count (DESC) using the provided OIDs ``conn_oids``.

        :param conn_oids: auto-reply module OIDs to be sorted
        :return: a cursor yielding auto-reply modules which ID is one of `conn_oids` from the most-used one
        """
        return self.find_cursor_with_count({OID_KEY: {"$in": conn_oids}},
                                           sort=[(AutoReplyModuleModel.CalledCount.key, pymongo.DESCENDING)])

    def get_module_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> ExtendedCursor[AutoReplyModuleModel]:
        """
        Get a list of modules in ``channel_oid`` sorted by used count (DESC) for stats.

        :param channel_oid: channel of the modules to get
        :param limit: maximum count of the result. No limit if not set or `None`
        :return: a cursor yielding auto-reply module from the most-used module
        """
        ret = self.find_cursor_with_count(
            {AutoReplyModuleModel.ChannelOid.key: channel_oid},
            sort=[(AutoReplyModuleModel.CalledCount.key, pymongo.DESCENDING)], limit=limit if limit else 0
        )

        return ret

    def get_unique_keyword_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> UniqueKeywordCountResult:
        pipeline = [
            {"$match": {AutoReplyModuleModel.ChannelOid.key: channel_oid}},
            {"$group": {
                OID_KEY: {
                    UniqueKeywordCountResult.KEY_WORD: "$" + AutoReplyModuleModel.KEY_KW_CONTENT,
                    UniqueKeywordCountResult.KEY_WORD_TYPE: "$" + AutoReplyModuleModel.KEY_KW_TYPE
                },
                UniqueKeywordCountResult.KEY_COUNT_USAGE: {"$sum": "$" + AutoReplyModuleModel.CalledCount.key},
                UniqueKeywordCountResult.KEY_COUNT_MODULE: {"$sum": 1}
            }},
            {"$sort": {
                UniqueKeywordCountResult.KEY_COUNT_USAGE: pymongo.DESCENDING,
                UniqueKeywordCountResult.KEY_COUNT_MODULE: pymongo.DESCENDING
            }}
        ]

        if limit:
            pipeline.append({"$limit": limit})

        return UniqueKeywordCountResult(self.aggregate(pipeline), limit)


class _AutoReplyModuleTagManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "tag"
    model_class = AutoReplyModuleTagModel

    def build_indexes(self):
        self.create_index(AutoReplyModuleTagModel.Name.key, name="Auto Reply Tag Identity", unique=True)

    def get_insert(self, name, color=ColorFactory.DEFAULT) -> AutoReplyModuleTagGetResult:
        ex = None
        tag_data: Optional[AutoReplyModuleTagModel] = self.find_one_casted(
            {AutoReplyModuleTagModel.Name.key: name},
            collation=case_insensitive_collation)

        if tag_data:
            outcome = GetOutcome.O_CACHE_DB
        else:
            model, outcome, ex = self.insert_one_data(Name=name, Color=color)

            if outcome.is_success:
                tag_data = model
                outcome = GetOutcome.O_ADDED
            else:
                outcome = GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT

        return AutoReplyModuleTagGetResult(outcome, ex, tag_data)

    def search_tags(self, tag_keyword: str) -> ExtendedCursor[AutoReplyModuleTagModel]:
        """
        Search the tags which contains ``tag_keyword``.

        The search is case-insensitive and ``tag_keyword`` can be a regex.

        :param tag_keyword: keyword to search the tag
        """
        return self.find_cursor_with_count(
            {AutoReplyModuleTagModel.Name.key: {"$regex": tag_keyword, "$options": "i"}},
            sort=[(OID_KEY, pymongo.DESCENDING)]
        )

    def get_tag_data(self, tag_oid: ObjectId) -> Optional[AutoReplyModuleTagModel]:
        return self.find_one_casted({OID_KEY: tag_oid})


class _AutoReplyManager(ClearableMixin):
    def __init__(self):
        self._mod = _AutoReplyModuleManager()
        self._tag = _AutoReplyModuleTagManager()

    def clear(self):
        self._mod.clear()
        self._tag.clear()

    def _get_tags_pop_score(self, filter_word: str = None, count: int = DataQuery.TagPopularitySearchCount) \
            -> List[AutoReplyTagPopularityScore]:
        """
        .. seealso::
            Time Past Weighting: https://www.desmos.com/calculator/db92kdecxa
            Appearance Weighting: https://www.desmos.com/calculator/a2uv5pqqku
        """
        pipeline = []
        filter_ = {
            AutoReplyModuleModel.TagIds.key: {"$in": [tag_data.id for tag_data in self._tag.search_tags(filter_word)]}
        }

        if filter_word:
            pipeline.append({"$match": filter_})

        pipeline.append({"$unwind": "$" + AutoReplyModuleModel.TagIds.key})
        pipeline.append({"$group": {
            OID_KEY: "$" + AutoReplyModuleModel.TagIds.key,
            AutoReplyTagPopularityScore.KEY_W_AVG_TIME_DIFF: {
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
                                                {"$toDate": "$" + OID_KEY}
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
            AutoReplyTagPopularityScore.KEY_APPEARANCE: {"$sum": 1}
        }})
        pipeline.append({"$addFields": {
            AutoReplyTagPopularityScore.KEY_W_APPEARANCE: {
                "$multiply": [
                    Database.PopularityConfig.AppearanceCoeffA,
                    {"$pow": [
                        "$" + AutoReplyTagPopularityScore.KEY_APPEARANCE,
                        Database.PopularityConfig.AppearanceFunctionCoeff
                    ]}
                ]
            }
        }})
        pipeline.append({"$addFields": {
            AutoReplyTagPopularityScore.SCORE: {
                "$subtract": [
                    {"$multiply": [
                        Database.PopularityConfig.AppearanceEquivalentWHr,
                        "$" + AutoReplyTagPopularityScore.KEY_W_APPEARANCE
                    ]},
                    "$" + AutoReplyTagPopularityScore.KEY_W_AVG_TIME_DIFF
                ]
            }
        }})
        pipeline.append({"$sort": {
            AutoReplyTagPopularityScore.SCORE: pymongo.DESCENDING
        }})
        pipeline.append({"$limit": count})

        return [AutoReplyTagPopularityScore.parse(doc) for doc in self._mod.aggregate(pipeline)]

    def add_conn(self, **kwargs) -> AutoReplyModuleAddResult:
        return self._mod.add_conn(**kwargs)

    def del_conn(self, keyword: str, channel_oid: ObjectId, remover_oid: ObjectId) -> UpdateOutcome:
        return self._mod.module_mark_inactive(keyword, channel_oid, remover_oid)

    def get_responses(
            self, keyword: str, keyword_type: AutoReplyContentType, channel_oid: ObjectId, *,
            update_async: bool = True) \
            -> List[Tuple[AutoReplyContentModel, bool]]:
        """
        Get the responses and a flag indicating
        if the content can be displayed without redirecting the user to visit the webpage.

        The flag is determined by the cooldown of the module. The content is **NOT** checked for this flag.

        :return: list of the responses and a redirection necessity flag
        """
        mod = self._mod.get_conn(keyword, keyword_type, channel_oid, update_async=update_async)
        resp_ctnt = []

        if mod:
            resp_ctnt = [(resp_mod, mod.cooldown_sec > AutoReply.BypassMultilineCDThresholdSeconds)
                         for resp_mod in mod.responses]

        return resp_ctnt

    def get_popularity_scores(self, search_keyword: str = None, count: int = DataQuery.TagPopularitySearchCount) \
            -> List[str]:
        """
        Get the :class:`list` of popular tag names sorted by the popularity score.
        """
        ret = []

        for pop_score in self._get_tags_pop_score(search_keyword, count):
            tag_data = self._tag.get_tag_data(pop_score.tag_id)
            if tag_data:
                ret.append(tag_data.name)

        return ret

    def tag_get_insert(self, name, color=ColorFactory.DEFAULT) -> AutoReplyModuleTagGetResult:
        return self._tag.get_insert(name, color)

    def get_conn_list(self, channel_oid: ObjectId, keyword: str = None, active_only: bool = True) \
            -> ExtendedCursor[AutoReplyModuleModel]:
        return self._mod.get_conn_list(channel_oid, keyword, active_only=active_only)

    def get_conn_list_oids(self, conn_oids: List[ObjectId]) -> ExtendedCursor[AutoReplyModuleModel]:
        return self._mod.get_conn_list_oids(conn_oids)

    def get_module_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> Generator[Tuple[Union[int, str], AutoReplyModuleModel], None, None]:
        return enumerate_ranking(self._mod.get_module_count_stats(channel_oid, limit),
                                 is_tie=lambda cur, prv: cur.called_count == prv.called_count)

    def get_unique_keyword_count_stats(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> UniqueKeywordCountResult:
        return self._mod.get_unique_keyword_count_stats(channel_oid, limit)


AutoReplyManager = _AutoReplyManager()
AutoReplyModuleManager = _AutoReplyModuleManager()
AutoReplyModuleTagManager = _AutoReplyModuleTagManager()
