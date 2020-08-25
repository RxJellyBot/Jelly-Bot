"""Module of various stats data manager."""
import traceback
from datetime import datetime, tzinfo, timedelta
from threading import Thread
from typing import Any, Optional, Union, List, Dict, Set

import pymongo
from bson import ObjectId

from env_var import is_testing
from extutils import dt_to_objectid
from extutils.checker import arg_type_ensure
from extutils.emailutils import MailSender
from extutils.dt import now_utc_aware, localtime, TimeRange
from extutils.locales import UTC, PytzInfo
from flags import APICommand, MessageType, BotFeature
from JellyBot.systemconfig import Database
from models import (
    APIStatisticModel, MessageRecordModel, OID_KEY, BotFeatureUsageModel,
    HourlyIntervalAverageMessageResult, DailyMessageResult, BotFeatureUsageResult, BotFeatureHourlyAvgResult,
    HourlyResult, BotFeaturePerUserUsageResult, MemberMessageByCategoryResult, MemberDailyMessageResult,
    MemberMessageCountResult, MeanMessageResultGenerator, CountBeforeTimeResult
)
from mongodb.factory.results import RecordAPIStatisticsResult, WriteOutcome
from mongodb.utils import ExtendedCursor
from ._base import BaseCollection

__all__ = ("APIStatisticsManager", "MessageRecordStatisticsManager", "BotFeatureUsageDataManager",)

DB_NAME = "stats"


class _APIStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "api"
    model_class = APIStatisticModel

    # pylint: disable=too-many-arguments

    @arg_type_ensure
    def record_stats(self, api_action: APICommand, sender_oid: ObjectId, parameter: dict, response: dict,
                     success: bool, org_param: dict, path_info: str, path_info_full: str) \
            -> RecordAPIStatisticsResult:
        """
        Record an API usage.

        :param api_action: action of the API call
        :param sender_oid: OID of the user who send the request
        :param parameter: parameter of the API call
        :param response: response of the API call
        :param success: if the response is successive
        :param org_param: original parameter of the API call
        :param path_info: `path_info` of the request
        :param path_info_full: path info got by calling `request.get_full_path_info()`
        :return: result of recording the API usage stats
        """
        entry, outcome, ex = self.insert_one_data(
            ApiAction=api_action, SenderOid=sender_oid, Parameter=parameter, Response=response, Success=success,
            Timestamp=datetime.utcnow(), PathInfo=path_info, PathInfoFull=path_info_full, PathParameter=org_param)

        return RecordAPIStatisticsResult(outcome, ex, entry)

    # pylint: enable=too-many-arguments


class _MessageRecordStatisticsManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "msg"
    model_class = MessageRecordModel

    # pylint: disable=too-many-arguments

    @arg_type_ensure
    def record_message(self, channel_oid: ObjectId, user_root_oid: Optional[ObjectId],
                       message_type: MessageType, message_content: Any, proc_time_secs: float) \
            -> WriteOutcome:
        """
        Record the message received.

        :param channel_oid: channel of the message
        :param user_root_oid: user who sent the message
        :param message_type: type of the message
        :param message_content: content of the message
        :param proc_time_secs: message processing time
        :return: outcome of the recording process
        """
        # Avoid casting `None` to `str`
        if message_content:
            # Truncate message content
            message_content = str(message_content)[:Database.MessageStats.MaxContentCharacter]

        _, outcome, _ = self.insert_one_data(
            ChannelOid=channel_oid, UserRootOid=user_root_oid, MessageType=message_type,
            MessageContent=message_content, ProcessTimeSecs=proc_time_secs
        )

        return outcome

    @arg_type_ensure
    def record_message_async(self, channel_oid: ObjectId, user_root_oid: Optional[ObjectId],
                             message_type: MessageType, message_content: Any,
                             proc_time_secs: float):
        """
        Same functionality as ``record_message()`` except that this method executes asynchronously.

        :param channel_oid: channel of the message
        :param user_root_oid: user who sent the message
        :param message_type: type of the message
        :param message_content: content of the message
        :param proc_time_secs: message processing time
        """
        if is_testing():
            # No async if testing
            self.record_message(channel_oid, user_root_oid, message_type, message_content, proc_time_secs)
        else:
            Thread(
                target=self.record_message,
                args=(channel_oid, user_root_oid, message_type, message_content, proc_time_secs)).start()

    # pylint: enable=too-many-arguments

    @arg_type_ensure
    def get_recent_messages(self, channel_oid: ObjectId, limit: Optional[int] = None) \
            -> ExtendedCursor[MessageRecordModel]:
        """
        Get recent messages in the ``channel_oid``.

        The returned messages will be sorted by its timestamp (DESC).

        If ``limit`` is ``None``, return all messages in the channel.

        :param channel_oid: channel of the returned messages
        :param limit: max count of the results
        :return: a cursor yielding messages in `channel_oid` from the most recent one
        """
        return self.find_cursor_with_count({MessageRecordModel.ChannelOid.key: channel_oid},
                                           sort=[(OID_KEY, pymongo.DESCENDING)], limit=limit if limit else 0)

    @arg_type_ensure
    def get_message_frequency(self, channel_oid: ObjectId, range_mins: Union[float, int, None] = None) -> float:
        """
        Get the message frequency in terms of seconds per message.

        The calculation is based on the earliest and the latest time of the record.

        If ``within_mins`` is specified, then it will be applied to the filter to get the data,
        counting backwards from the current datetime.

        :param channel_oid: message of the channel
        :param range_mins: time range in minutes for the calculation
        :return: sec / message
        """
        filter_ = {MessageRecordModel.ChannelOid.key: channel_oid}

        if range_mins:
            filter_[OID_KEY] = {"$gt": ObjectId.from_datetime(now_utc_aware() - timedelta(minutes=range_mins))}

        rct_msg_count = self.count_documents(filter_)

        # Early termination if no message
        if rct_msg_count == 0:
            return 0.0

        # Calculate time range
        earliest = self.find_one(filter_, sort=[(OID_KEY, pymongo.ASCENDING)])
        if not earliest:
            return 0.0

        latest = self.find_one(filter_, sort=[(OID_KEY, pymongo.DESCENDING)])

        range_mins = (latest[OID_KEY].generation_time - earliest[OID_KEY].generation_time).total_seconds() / 60

        return range_mins / rct_msg_count

    def get_user_last_message_ts(self, channel_oid: ObjectId, user_oids: List[ObjectId], tzinfo_: tzinfo = None) \
            -> Dict[ObjectId, datetime]:
        """
        Get the last message timestamps of ``user_oids`` :class:`dict` in ``channel_oid``.

        This method uses ``localtime()`` to localize the timestamps.

        :param channel_oid: channel to get the last message timestamps
        :param user_oids: user OIDs to get the last message timestamps
        :param tzinfo_: timezone info to be used to localize the timestamps
        :return: a `dict` which key is the user OID and value is their last message timestamp
        """
        ret = {}
        key_ts = "msgts"

        pipeline = [
            {"$match": {
                MessageRecordModel.ChannelOid.key: channel_oid,
                MessageRecordModel.UserRootOid.key: {"$in": user_oids}
            }},
            {"$sort": {
                "_id": pymongo.DESCENDING
            }},
            {"$group": {
                "_id": "$" + MessageRecordModel.UserRootOid.key,
                key_ts: {"$first": "$" + OID_KEY}
            }}
        ]
        for data in self.aggregate(pipeline):
            ret[data[OID_KEY]] = localtime(data[key_ts].generation_time, tzinfo_)

        return ret

    # Statistics

    @staticmethod
    def _channel_oids_filter(channel_oids: Union[ObjectId, List[ObjectId]]):
        if isinstance(channel_oids, ObjectId):
            return {MessageRecordModel.ChannelOid.key: channel_oids}

        if isinstance(channel_oids, list):
            return {MessageRecordModel.ChannelOid.key: {"$in": channel_oids}}

        raise ValueError("Must be either `ObjectId` or `List[ObjectId]`.")

    def get_channel_last_message_ts(self, user_oid: ObjectId, channel_oids: Union[ObjectId, List[ObjectId]]) \
            -> Dict[ObjectId, datetime]:
        """
        Get the last message timestamp of ``channel_oids`` of ``user_oid``.

        Key of the returned :class:`dict` is channel OID and value is the timestamp of the last message.

        If there's a channel that the user has not sent any message in it, the returned :class:`dict` will **NOT**
        have a key for this channel.

        :param user_oid: OID of the user to get the timestamps
        :param channel_oids: OID of the channel(s) to get the timestamps
        :return: a `dict` which key is channel OIDs and value is the last message timestamp
        """
        filter_ = self._channel_oids_filter(channel_oids)
        filter_[MessageRecordModel.UserRootOid.key] = user_oid
        key_last_timestamp = "last_ts"
        ret = {}

        aggr_pipeline = [
            {
                "$match": filter_
            },
            {
                "$group": {
                    OID_KEY: "$" + MessageRecordModel.ChannelOid.key,
                    key_last_timestamp: {"$max": "$" + OID_KEY}
                }
            }
        ]

        for data in self.aggregate(aggr_pipeline):
            ret[data[OID_KEY]] = localtime(data[key_last_timestamp].generation_time)

        return ret

    def get_messages_distinct_channel(self, message_fragment: str) -> Set[ObjectId]:
        """
        Get the channel OIDs where any of the messages in it contain ``message_fragment``.

        :param message_fragment: message fragment to search
        :return: a set of channel OIDs where any of the messages contain `message_fragment`
        """
        aggr = list(self.aggregate([
            {"$match": {
                MessageRecordModel.MessageContent.key: {"$regex": message_fragment, "$options": "i"}
            }},
            {"$group": {
                OID_KEY: None,
                "cid": {"$addToSet": "$" + MessageRecordModel.ChannelOid.key}
            }},
            {"$unwind": "$cid"},
            {"$project": {
                OID_KEY: 0
            }}
        ]))

        return {e["cid"] for e in aggr}

    @staticmethod
    def _get_user_messages_total_count_switch_branches(trange: TimeRange):
        """Get the ``$switch`` branch for MongoDB aggregation pipeline to separate the stats by days."""
        # $switch expression for time range
        switch_branches = []

        # Check for full range (inf)
        # `start` and `end` cannot be `None` for generating `ObjectId`,
        # however `start` and `end` for full range are `None`.
        if not trange.is_inf:
            for idx, range_ in enumerate(trange.get_periods()):
                start_id = dt_to_objectid(range_.start)
                if not start_id:
                    continue
                end_id = dt_to_objectid(range_.end)
                if not end_id:
                    continue

                switch_branches.append(
                    {"case": {"$and": [{"$gte": ["$" + OID_KEY, start_id]},
                                       {"$lt": ["$" + OID_KEY, end_id]}]},
                     "then": str(idx)}
                )

        return switch_branches

    def get_user_messages_total_count(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                                      hours_within: Optional[int] = None,
                                      start: Optional[datetime] = None, end: Optional[datetime] = None,
                                      period_count: int = 3,
                                      tzinfo_: Optional[tzinfo] = None) \
            -> MemberMessageCountResult:
        """
        Get the total count of the users in ``channel_oids`` as a :class:`MemberMessageCountResult`.

        :param channel_oids: channel OIDs to get the total message count
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param period_count: count of periods of the data
        :param tzinfo_: timezone info to be used for separating days and ranging the data
        :return: a `MemberMessageCountResult` containing the message counts of users in `channel_oids`
        """
        match_d = self._channel_oids_filter(channel_oids)
        trange = TimeRange(range_hr=hours_within, start=start, end=end, range_mult=period_count, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        # $switch expression for time range
        switch_branches = self._get_user_messages_total_count_switch_branches(trange)

        group_key = {MemberMessageCountResult.KEY_MEMBER_ID: "$" + MessageRecordModel.UserRootOid.key}
        if switch_branches:
            group_key[MemberMessageCountResult.KEY_INTERVAL_IDX] = {
                "$switch": {
                    "branches": switch_branches,

                    # Set `default` to the highest index to handle the only missed case because of `low <= x < high`
                    # where `high` is inclusive for the function but not handled
                    "default": str(len(trange.get_periods()) - 1)
                }
            }

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: group_key,
                MemberMessageCountResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberMessageCountResult(list(self.aggregate(aggr_pipeline)), period_count, trange)

    def get_user_messages_by_category(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                                      hours_within: Optional[int] = None,
                                      start: Optional[datetime] = None, end: Optional[datetime] = None,
                                      tzinfo_: Optional[tzinfo] = None) \
            -> MemberMessageByCategoryResult:
        """
        Get user messages categorized by the message content type in ``channel_oids``.

        :param channel_oids: channel OIDs to get the message
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param tzinfo_: timezone info to be used for separating days and ranging the data
        :return: a `MemberMessageByCategoryResult` containing the categorized user message count in `channel_oids`
        """
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        aggr_pipeline = [
            {"$match": match_d},
            {"$group": {
                OID_KEY: {
                    MemberMessageByCategoryResult.KEY_MEMBER_ID: "$" + MessageRecordModel.UserRootOid.key,
                    MemberMessageByCategoryResult.KEY_CATEGORY: "$" + MessageRecordModel.MessageType.key
                },
                MemberMessageByCategoryResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberMessageByCategoryResult(list(self.aggregate(aggr_pipeline)))

    def hourly_interval_message_count(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                                      tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
                                      start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> HourlyIntervalAverageMessageResult:
        """
        Get hourly message count in ``channel_oids``.

        :param channel_oids: channel OIDs to get the message
        :param tzinfo_: timezone info to be used for ranging and separating the data
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: a `HourlyIntervalAverageMessageResult` containing the hourly message count of each days
        """
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    HourlyIntervalAverageMessageResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}},
                    HourlyIntervalAverageMessageResult.KEY_CATEGORY:
                        "$" + MessageRecordModel.MessageType.key
                },
                HourlyIntervalAverageMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return HourlyIntervalAverageMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            end_time=end
        )

    def daily_message_count(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                            tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
                            start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> DailyMessageResult:
        """
        Get daily message count in ``channel_oids``.

        :param channel_oids: channel OIDs to get the message
        :param tzinfo_: timezone info to be used for ranging and separating the data
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: a `DailyMessageResult` containing the daily message count in `channel_oids`
        """
        match_d = self._channel_oids_filter(channel_oids)
        self.attach_time_range(match_d, hours_within=hours_within, start=start, end=end, tzinfo_=tzinfo_)
        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    DailyMessageResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": DailyMessageResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    },
                    DailyMessageResult.KEY_HOUR: {
                        "$hour": {
                            "date": "$_id",
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                DailyMessageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return DailyMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            tzinfo_,
            start=start, end=end)

    def mean_message_count(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                           tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
                           start: Optional[datetime] = None, end: Optional[datetime] = None,
                           max_mean_days: int = 5) \
            -> MeanMessageResultGenerator:
        """
        Get a :class:`MeanMessageResultGenerator` which generates the average daily message count in ``channel_oids``.

        Set ``max_mean_days`` appropriately (only set the actual days that will be requested) to reduce performance
        waste on both getting the data and generating the results.

        :param channel_oids: channel OIDs to get the message
        :param tzinfo_: timezone info to be used for ranging and separating the data
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param max_mean_days: max mean days that might be requested on the returned `MeanMessageResultGenerator`
        :return: a `MeanMessageResultGenerator` which generates average message count results
        """
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)
        # Pushing back the starting time to calculate the mean data at `start`.
        trange.set_start_day_offset(-max_mean_days)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    MeanMessageResultGenerator.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": MeanMessageResultGenerator.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                MeanMessageResultGenerator.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return MeanMessageResultGenerator(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=trange.start_org, end=end),
            tzinfo_,
            trange=trange, max_mean_days=max_mean_days)

    def message_count_before_time(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                                  tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
                                  start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> CountBeforeTimeResult:
        """
        Get the message count in ``channel_oids`` before ``end``.

        ``end`` will be filled with current time if not specified or ``None``.

        :param channel_oids: channel OIDs to get the message
        :param tzinfo_: timezone info to be used for ranging and separating the data
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: a `CountBeforeTimeResult` containing the daily message count before `end` in `channel_oids`
        """
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$project": {
                CountBeforeTimeResult.KEY_SEC_OF_DAY: {
                    "$add": [
                        {"$multiply": [{"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}, 3600]},
                        {"$multiply": [{"$minute": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}, 60]},
                        {"$second": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}
                    ]
                }
            }},
            {"$match": {
                CountBeforeTimeResult.KEY_SEC_OF_DAY: {"$lt": trange.end_time_seconds}
            }},
            {"$group": {
                "_id": {
                    CountBeforeTimeResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": CountBeforeTimeResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    }
                },
                CountBeforeTimeResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {"_id": pymongo.ASCENDING}}
        ]

        return CountBeforeTimeResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=trange.start_org, end=end),
            tzinfo_,
            trange=trange)

    def member_daily_message_count(self, channel_oids: Union[ObjectId, List[ObjectId]], *,
                                   tzinfo_: PytzInfo = UTC.to_tzinfo(), hours_within: Optional[int] = None,
                                   start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> MemberDailyMessageResult:
        """
        Get the daily message count of each members in ``channel_oids``.

        :param channel_oids: channel OIDs to get the message
        :param tzinfo_: timezone info to be used for ranging and separating the data
        :param hours_within: hour range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: a `MemberDailyMessageResult` containing the daily message count of each members in `channel_oids`
        """
        match_d = self._channel_oids_filter(channel_oids)

        trange = TimeRange(range_hr=hours_within, start=start, end=end, tzinfo_=tzinfo_)

        self.attach_time_range(match_d, trange=trange)

        pipeline = [
            {"$match": match_d},
            {"$group": {
                "_id": {
                    MemberDailyMessageResult.KEY_DATE: {
                        "$dateToString": {
                            "date": "$_id",
                            "format": MemberDailyMessageResult.FMT_DATE,
                            "timezone": tzinfo_.tzidentifier
                        }
                    },
                    MemberDailyMessageResult.KEY_MEMBER: "$" + MessageRecordModel.UserRootOid.key
                },
                MemberDailyMessageResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return MemberDailyMessageResult(
            list(self.aggregate(pipeline)),
            HourlyResult.data_days_collected(self, match_d, hr_range=hours_within, start=start, end=end),
            tzinfo_,
            trange=trange)


class _BotFeatureUsageDataManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "bot"
    model_class = BotFeatureUsageModel

    @arg_type_ensure
    def record_usage(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        """
        Record a bot feature usage if ``feature_used`` is not :class:`BotFeature.UNDEFINED`.

        If :class:`BotFeature.UNDEFINED` is called, the activity will not be logged.
        Instead, an email report will be sent.

        :param feature_used: bot feature used
        :param channel_oid: channel where the feature was used
        :param root_oid: user who uses the feature
        """
        if feature_used == BotFeature.UNDEFINED:
            content = f"Undefined bot command sent by:\n" \
                      f"<code>{root_oid}</code> in channel <code>{channel_oid}</code>\n" \
                      f"<hr>" \
                      f"<pre>Traceback:\n" \
                      f"{traceback.format_exc()}</pre>"

            MailSender.send_email_async(content, subject="Undefined bot command called")
            return

        self.insert_one_data(Feature=feature_used, ChannelOid=channel_oid, SenderRootOid=root_oid)

    @arg_type_ensure
    def record_usage_async(self, feature_used: BotFeature, channel_oid: ObjectId, root_oid: ObjectId):
        """
        Same functionality as ``record_usage()`` except that this method executes asynchronously.

        :param feature_used: bot feature used
        :param channel_oid: channel where the feature was used
        :param root_oid: user who uses the feature
        """
        if is_testing():
            self.record_usage(feature_used, channel_oid, root_oid)
        else:
            Thread(target=self.record_usage, args=(feature_used, channel_oid, root_oid)).start()

    # Statistics

    @arg_type_ensure
    def get_channel_usage(self, channel_oid: ObjectId, *, hours_within: int = None, incl_not_used: bool = False) \
            -> BotFeatureUsageResult:
        """
        Get the bot feature usage in ``channel_oid``.

        Returned data will be sorted by the usage count (DESC) then the feature code (ASC).

        :param channel_oid: channel to get the usage stats
        :param hours_within: hour range of the data
        :param incl_not_used: whether to include the features that are not used in `channel_oid`
        :return: a `BotFeatureUsageResult` containing the bot feature usage data in `channel_oid`
        """
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self.attach_time_range(filter_, hours_within=hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: "$" + BotFeatureUsageModel.Feature.key,
                BotFeatureUsageResult.KEY_COUNT: {"$sum": 1}
            }},
            {"$sort": {
                BotFeatureUsageResult.KEY_COUNT: pymongo.DESCENDING,
                OID_KEY: pymongo.ASCENDING
            }}
        ]

        return BotFeatureUsageResult(list(self.aggregate(pipeline)), incl_not_used)

    @arg_type_ensure
    def get_channel_hourly_avg(self, channel_oid: ObjectId, *,
                               hours_within: int = None, incl_not_used: bool = False,
                               tzinfo_: PytzInfo = UTC.to_tzinfo()) \
            -> BotFeatureHourlyAvgResult:
        """
        Get hourly average use of the bot features in ``channel_oid``.

        :class:`BotFeature.UNDEFINED` will **NOT** be included in the result even if ``incl_not_used`` is ``True``.

        Returned data will be sorted by the feature code (ASC).

        :param channel_oid: channel to get the usage stats
        :param hours_within: hour range of the data
        :param incl_not_used: whether to include the features that are not used in `channel_oid`
        :param tzinfo_: timezone info to be used for separating the data
        :return: a `BotFeatureHourlyAvgResult` containing the hourly usage of the data in `channel_oid`
        """
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        self.attach_time_range(filter_, hours_within=hours_within, tzinfo_=tzinfo_)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: {
                    BotFeatureHourlyAvgResult.KEY_FEATURE:
                        "$" + BotFeatureUsageModel.Feature.key,
                    BotFeatureHourlyAvgResult.KEY_HR:
                        {"$hour": {"date": "$_id", "timezone": tzinfo_.tzidentifier}}
                },
                BotFeatureHourlyAvgResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        # Not using $sort stage because the data will be sorted locally.
        #
        # The reason of sorting it locally is because that if `incl_not_used` is enabled, a `set.difference()`
        # operation will be executed to find the features that are not being used.

        return BotFeatureHourlyAvgResult(
            list(self.aggregate(pipeline)),
            incl_not_used,
            HourlyResult.data_days_collected(self, filter_, hr_range=hours_within)
        )

    @arg_type_ensure
    def get_channel_per_user_usage(self, channel_oid: ObjectId, *,
                                   hours_within: int = None, member_oid_list: Optional[List[ObjectId]] = None) \
            -> BotFeaturePerUserUsageResult:
        """
        Get the per user usage data in ``channel_oid``.

        If ``member_oid_list`` is not ``None``, limit the result to only display the usage of the given users.
        Otherwise, return all usages from the members of ``channel_oid``.

        If there are any user that has not used any of the bot feature, they will **NOT** be included in the result.

        Returned data will include the features that are not being used by the corresponding user.

        :param channel_oid: channel to get the usage stats
        :param hours_within: hour range of the data
        :param member_oid_list: members to get the data
        :return: a `BotFeaturePerUserUsageResult` containing the usage data of each members in `channel_oid`
        """
        filter_ = {BotFeatureUsageModel.ChannelOid.key: channel_oid}

        if member_oid_list:
            filter_[BotFeatureUsageModel.SenderRootOid.key] = {"$in": member_oid_list}

        self.attach_time_range(filter_, hours_within=hours_within)

        pipeline = [
            {"$match": filter_},
            {"$group": {
                OID_KEY: {
                    BotFeaturePerUserUsageResult.KEY_FEATURE:
                        "$" + BotFeatureUsageModel.Feature.key,
                    BotFeaturePerUserUsageResult.KEY_UID:
                        "$" + BotFeatureUsageModel.SenderRootOid.key
                },
                BotFeaturePerUserUsageResult.KEY_COUNT: {"$sum": 1}
            }}
        ]

        return BotFeaturePerUserUsageResult(list(self.aggregate(pipeline)))


APIStatisticsManager = _APIStatisticsManager()
MessageRecordStatisticsManager = _MessageRecordStatisticsManager()
BotFeatureUsageDataManager = _BotFeatureUsageDataManager()
