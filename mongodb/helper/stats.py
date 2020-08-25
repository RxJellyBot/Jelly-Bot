"""Implementations of the helper to integrate the process of getting the stats."""
import math
from collections import namedtuple
from dataclasses import dataclass, field, InitVar
from datetime import tzinfo, datetime
from typing import List, Optional, Union, NamedTuple, Dict

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware, localtime
from extutils.utils import enumerate_ranking
from flags import BotFeature, MessageType
from models import (
    ChannelModel, ChannelCollectionModel, MessageRecordModel,
    MemberMessageByCategoryResult, MemberMessageCountResult, MemberDailyMessageResult
)
from mongodb.factory import (
    MessageRecordStatisticsManager, ProfileManager, BotFeatureUsageDataManager
)

from .search import IdentitySearcher


# region Dataclasses for `MessageStatsDataProcessor`
@dataclass
class UserMessageStatsEntry:
    """Entry of ``member_stats`` in :class:`UserMessageStats`."""

    user_oid: ObjectId
    user_name: str
    available: bool
    total_count: int
    total_count_ratio: float
    category_count: List[NamedTuple]
    rank: int = field(default=1, init=False)

    @property
    def ratio_pct_str(self) -> str:
        """
        Get the total message count ratio among others as a string formatted with ``.02%``.

        :return: total message count ratio among others as a string
        """
        return f"{self.total_count_ratio:.02%}"

    def set_rank(self, rank: int):
        """
        Set the rank of this entry.

        :param rank: rank of this entry
        """
        self.rank = rank


@dataclass
class UserMessageStats:
    """
    Collection of the stats of all members in the specific channel.

    ``msg_count`` is the total message count of ``member_stats``.
    """

    org_stats: InitVar[List[UserMessageStatsEntry]]
    member_stats: List[UserMessageStatsEntry] = field(init=False)
    msg_count: int
    label_category: List[MessageType]

    def __post_init__(self, org_stats: List[UserMessageStatsEntry]):
        """
        Post initialization of :class:`UserMessageStats`.

        ``org_stats`` will be used to get and attach the rank to the entry,
        then these entries will be the data of ``member_stats``.

        :param org_stats: original stats to be used for constructing a sorted stats
        """
        self.member_stats = []
        # Disabling T-prefix for datatable sorting in the webpage
        for rank, data in enumerate_ranking(
                list(sorted(org_stats, key=lambda x: x.total_count, reverse=True)),
                is_tie=lambda cur, prv: cur.total_count == prv.total_count,
                t_prefix=False):
            data.set_rank(rank)
            self.member_stats.append(data)


@dataclass
class UserMessageRanking:
    """Object represents a single rank in the channel."""

    rank: int
    total: int

    @property
    def available(self) -> bool:
        """
        Check if the rank is available.

        :return: if the rank is available
        """
        return self.rank > -1

    def __str__(self):
        return f"#{self.rank} / #{self.total}" if self.available else _("Unavailable")


@dataclass
class HandledMessageRecordEntry:
    """Represents a handled/processed message record. Also an entry of ``data`` in :class:`HandledMessageRecords`."""

    model: MessageRecordModel
    user_name: str
    timestamp: str = field(init=False)
    content_type: MessageType = field(init=False)
    content_html: str = field(init=False)
    process_time_ms: float = field(init=False)

    tz: InitVar[Optional[tzinfo]]

    def __post_init__(self, tz: Optional[tzinfo]):
        """
        Post initialization of ``HandledMessageRecordEntry``.

        :param tz: timezone to be used for timestamp
        """
        self.timestamp = localtime(ObjectId(self.model.id).generation_time, tz).strftime("%Y-%m-%d %H:%M:%S")
        self.content_type = self.model.message_type
        self.content_html = self.model.message_content.replace("\n", "<br>")
        self.process_time_ms = self.model.process_time_secs * 1000


@dataclass
class HandledMessagesComposition:
    """An object representing the message composition of the given channel(s)."""

    label_type: List[MessageType] = field(init=False, default_factory=list)
    label_count: List[int] = field(init=False, default_factory=list)

    counter_obj: InitVar[Dict[MessageType, int]]

    def __post_init__(self, counter_obj: Dict[MessageType, int]):
        """
        Post initialization of :class:`HandledMessagesComposition`.

        This loop through ``counter_obj`` to add things to ``label_type`` and ``label_count`` for webpage rendering.

        :param counter_obj: message counter of the given channel(s)
        """
        for cat, count in counter_obj.items():
            self.label_type.append(cat.key)
            self.label_count.append(count)


@dataclass
class HandledMessageRecords:
    """Represents a collection of handled messages and its related stats."""

    data: List[HandledMessageRecordEntry]
    avg_processing_secs: Dict[MessageType, float] = field(init=False, default_factory=dict)
    message_frequency = float
    unique_sender_count: int = field(init=False, default_factory=int)
    msg_composition: HandledMessagesComposition = field(init=False, default=HandledMessagesComposition({}))

    def __post_init__(self):
        """
        Post initialization of :class:`HandledMessageRecords`.

        This calculates average message handling time, checks the count of unique message senders and
        calculates the message frequency.
        """
        msg_count = len(self.data)

        proc_secs = [msg.model.process_time_secs for msg in self.data]
        self.avg_processing_secs = sum(proc_secs) / msg_count

        counter = {mt: 0 for mt in MessageType}
        for entry in self.data:
            counter[MessageType.cast(entry.model.message_type)] += 1
        self.msg_composition = HandledMessagesComposition(counter)

        self.unique_sender_count = len({data.model.user_root_oid for data in self.data})

        if self.data:
            self.message_frequency = \
                (now_utc_aware() - self.data[-1].model.id.generation_time).total_seconds() / msg_count
        else:
            self.message_frequency = 0.0


@dataclass
class UserDailyMessageEntry:
    """
    Entry of :class:`UserDailyMessageResult`.

    Each element of either ``count_list`` or ``rank_list`` represents the count / rank of each days.
    """

    member_name: str
    available: bool
    count_list: List[int]
    rank_list: List[str]
    count_total: int = field(init=False)

    def __post_init__(self):
        """
        Post initialization of :class:`UserDailyMessageEntry`.

        Calculates the total message count of a user and store it to ``count_total``.
        """
        self.count_total = sum(self.count_list)

    @property
    def rank_count_zip(self):
        """
        Get a zip generator which yields the rank and the message count of a day simultaneously.

        Rank will be the 1st object to be yielded and the message count is the 2nd object.

        :return: a zip generator yielding one rank and one count at the same time
        """
        return zip(self.rank_list, self.count_list)


@dataclass
class UserDailyMessageResult:
    """Collection of user daily message counts as :class:`UserDailyMessageEntry` with some stats."""

    label_dates: List[str]
    active_members: List[int]
    entries: List[UserDailyMessageEntry]

    @property
    def label_dates_jsarr(self) -> str:
        """
        Get the date labels (``label_dates``) as a string to use it in javascript as an array.

        :return: date labels as a string for js array
        """
        return f"[{self.label_dates}]"


@dataclass
class UserMessageCountIntervalEntry:
    """
    Entry of ``UserMessageCountIntervalResult`` with some stats.

    ------------

    There are some special stats introduced here:

    **Difference Index (DI) [1]**

    This calculates the difference between 2 adjacent intervals,
    and use that difference times the 4th root of (interval index / interval count) [2],
    then accumulate the result to the index.

    The smaller the index, the smaller the message count change.

    [1] The growth of this index depends more on the recent difference change.

    [2] Doing so will create the deteriorating effect for older difference.

    **Bounce**

    Formula::

        sum(abs(differences between intervals)) / max(len(differences between intervals), 1)
    """

    # pylint: disable=too-many-instance-attributes

    id: int = field(init=False)
    """Unique identifier used for identifying individual result graph in `msg_chart_count_trange.html`"""
    user_name: str
    total: int
    count: List[int]
    """Will be used to render the small chart."""
    count_new_front: List[int] = field(init=False)
    """Will be used for rendering the datatable."""
    diff_index: float = 0.0
    diff_index_nrm: float = 0.0
    bounce: float = field(init=False)

    # pylint: enable=too-many-instance-attributes

    def __post_init__(self):
        """
        Post initialization of :class:`UserMessageCountIntervalEntry`.

        Get a unique identifier for graphs, reverse the count data for webpage rendering,
        calculate the difference index [1][2] then calculate the bounce [3] of the user.

        [1][3] Check the class documentation for more details on the stats.
        [2] Both w/ and w/o normalizing will be calculated.
        """
        # Put ID
        self.id = id(self)

        # Reverse to put the most recent at the front
        self.count_new_front = list(reversed(self.count))

        bounce = []
        difference = []

        item_count = len(self.count)

        for idx in range(1, item_count):
            base = self.count[idx - 1]
            data = self.count[idx]

            diff = data - base

            difference.append(diff)
            bounce.append(abs(diff))
            self.diff_index += diff * math.pow(idx / item_count, 1 / 4)

        self.diff_index_nrm = self.diff_index / (abs(max(bounce)) or 1) * 1000
        self.bounce = sum(bounce) / (len(bounce) or 1)


@dataclass
class UserMessageCountIntervalResult:
    """Collection of :class:`UserMessageCountIntervalEntry` with some related stats or info packed."""

    original_result: InitVar[MemberMessageCountResult]
    uname_dict: InitVar[Dict[ObjectId, str]]
    available_only: InitVar[bool]
    time_ranges: List[str] = field(init=False)
    data: List[UserMessageCountIntervalEntry] = field(init=False)
    is_inf: bool = field(init=False)

    def __post_init__(self, original_result: MemberMessageCountResult, uname_dict: Dict[ObjectId, str],
                      available_only: bool):
        """
        Post initialization of :class:`UserMessageCountIntervalResult`.

        This reverses the time ranges in ``original_result``,
        then process the data in ``original_result`` to ``data``.

        If there are some names found in ``uname_dict`` but not in ``original_result``,
        the data of these users will be filled with 0s.

        :param original_result: original message count results to be processed
        :param uname_dict: a `dict` for user ID-name conversion
        :param available_only: if `original_result` only contains available members
        """
        # Reverse to put the most recent at the front
        self.time_ranges = \
            list(reversed([trange.expr_period_short for trange in original_result.trange.get_periods()]))

        self.is_inf = original_result.trange.is_inf

        self.data = []
        for uid, entry in original_result.data.items():
            uname = uname_dict.pop(uid, None)

            if not uname and available_only:
                continue

            self.data.append(UserMessageCountIntervalEntry(user_name=uname, total=entry.total, count=entry.count))

        # Fill 0
        if uname_dict:
            for uid, name in uname_dict.items():
                entry = UserMessageCountIntervalEntry(user_name=name, total=0, count=[0] * original_result.interval)
                self.data.append(entry)


# endregion


class MessageStatsDataProcessor:
    """Class to integrate the operations of getting the message stats and process them for webpage rendering."""

    @staticmethod
    def _get_user_msg_stats(msg_result: MemberMessageByCategoryResult,
                            ch_data: Union[ChannelModel, ChannelCollectionModel] = None,
                            available_only: bool = True) -> UserMessageStats:
        # pylint: disable=too-many-locals

        entries: List[UserMessageStatsEntry] = []

        if isinstance(ch_data, ChannelModel):
            ch_oids = [ch_data.id]
        elif isinstance(ch_data, ChannelCollectionModel):
            ch_oids = ch_data.child_channel_oids
        else:
            raise ValueError(f"The type of `ch_data` must either be `ChannelModel` or `ChannelCollectionModel`. "
                             f"({type(ch_data)})")

        msg_rec = {}
        available_dict = {}
        for member in ProfileManager.get_channel_prof_conn(ch_oids, available_only=available_only):
            msg_rec[member.user_oid] = msg_result.data.get(member.user_oid, msg_result.gen_new_data_entry())
            available_dict[member.user_oid] = member.available

        if not msg_rec:
            return UserMessageStats(org_stats=[], msg_count=0, label_category=msg_result.LABEL_CATEGORY)

        individual_msgs = [vals.total for vals in msg_rec.values()]
        max_individual_msg: int = max(individual_msgs)

        uid_handled = IdentitySearcher.get_batch_user_name(msg_rec, ch_data, on_not_found="(N/A)")

        for uid, name in uid_handled.items():
            data_cat = msg_rec[uid]

            sum_ = data_cat.total

            cat_count = []
            CategoryEntry = namedtuple("CategoryEntry", ["count", "percentage"])
            for cat in msg_result.LABEL_CATEGORY:
                count = data_cat.get_count(cat)
                cat_count.append(CategoryEntry(count=count, percentage=count / sum_ * 100 if sum_ > 0 else 0))

            entries.append(
                UserMessageStatsEntry(
                    user_oid=uid, user_name=name, category_count=cat_count, available=available_dict[uid],
                    total_count=sum_, total_count_ratio=sum_ / max_individual_msg if max_individual_msg > 0 else 0
                )
            )

        # pylint: enable=too-many-locals

        return UserMessageStats(org_stats=entries, msg_count=sum(individual_msgs),
                                label_category=msg_result.LABEL_CATEGORY)

    @staticmethod
    def _get_user_msg_ranking(channel_oids: Union[List[ObjectId], ObjectId], root_oid: ObjectId, *,
                              hours_within: Optional[int] = None, start: Optional[datetime] = None,
                              end: Optional[datetime] = None) \
            -> UserMessageRanking:
        msg_by_cat = MessageRecordStatisticsManager.get_user_messages_by_category(
            channel_oids, hours_within=hours_within, start=start, end=end)

        data = sorted(msg_by_cat.data.items(), key=lambda _: _[1].total, reverse=True)
        for idx, item in enumerate(data, start=1):
            oid, _ = item
            if oid == root_oid:
                return UserMessageRanking(rank=idx, total=len(data))

        return UserMessageRanking(rank=-1, total=len(data))

    @staticmethod
    def _get_user_daily_entries(result: MemberDailyMessageResult, uname_dict: Dict[ObjectId, str]):
        actv_mbr = []  # Array to store active member count
        proc_count = {oid: [] for oid in uname_dict}  # Array for message count of each days of a member
        proc_rank = {oid: [] for oid in uname_dict}  # Array for message count rank of each days of a member

        for date in result.dates:
            # Get the data of the corresponding date
            data_of_date = result.data_count[date]

            # Storing active member count
            actv_mbr.append(len(data_of_date))

            # Get and sort the daily message count
            collated_count = {oid: data_of_date.get(oid, 0) for oid in proc_count}
            sorted_count = list(sorted(collated_count.items(), key=lambda x: x[1], reverse=True))

            # Insert daily count and rank
            for rank, entry in enumerate_ranking(sorted_count, is_tie=lambda cur, prv: cur[1] == prv[1]):
                uid, count = entry
                proc_count[uid].append(count)
                proc_rank[uid].append(rank)

        return actv_mbr, proc_count, proc_rank

    @staticmethod
    def get_user_daily_message(channel_data: ChannelModel, *,
                               hours_within: Optional[int] = None, start: Optional[datetime] = None,
                               end: Optional[datetime] = None, tz: Optional[tzinfo] = None,
                               available_only: Optional[bool] = True) \
            -> UserDailyMessageResult:
        """
        Get processed user daily message count.

        :param channel_data: channel to get the user daily message count
        :param hours_within: time range of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param tz: timezone info to apply to the data
        :param available_only: if to get the stats from available members only
        :return: a `UserDailyMessageResult`
        """
        available_dict = {prof_conn.user_oid: prof_conn.available for prof_conn
                          in ProfileManager.get_channel_prof_conn(channel_data.id, available_only=available_only)}
        uname_dict = IdentitySearcher.get_batch_user_name(list(available_dict), channel_data, on_not_found="(N/A)")
        result = MessageRecordStatisticsManager.member_daily_message_count(
            channel_data.id, hours_within=hours_within, start=start, end=end, tzinfo_=tz)

        # Array for storing active member count
        actv_mbr, proc_count, proc_rank = MessageStatsDataProcessor._get_user_daily_entries(result, uname_dict)

        entries = [
            UserDailyMessageEntry(
                member_name=name, count_list=proc_count[oid], rank_list=proc_rank[oid], available=available_dict[oid])
            for oid, name in uname_dict.items()
        ]

        return UserDailyMessageResult(label_dates=result.dates, entries=entries, active_members=actv_mbr)

    @staticmethod
    def get_user_channel_messages(channel_data: ChannelModel, *,
                                  hours_within: Optional[int] = None, start: Optional[datetime] = None,
                                  end: Optional[datetime] = None, available_only: bool = True) \
            -> UserMessageStats:
        """
        Get the processed message count categorized by message type in ``channel_data``.

        :param channel_data: channel to get the message stats
        :param hours_within: time range in hours for the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param available_only: if to only get the stats of available members
        :return: a `UserMessageStats` containing the processed data
        """
        return MessageStatsDataProcessor._get_user_msg_stats(
            MessageRecordStatisticsManager.get_user_messages_by_category(
                channel_data.id, hours_within=hours_within, start=start, end=end),
            channel_data, available_only
        )

    @staticmethod
    def get_user_chcoll_messages(chcoll_data: ChannelCollectionModel, *,
                                 hours_within: Optional[int] = None, start: Optional[datetime] = None,
                                 end: Optional[datetime] = None, available_only: bool = True) \
            -> UserMessageStats:
        """
        Get the processed message count categorized by message type in ``chcoll_data``.

        :param chcoll_data: channel collection to get the message stats
        :param hours_within: time range in hours for the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param available_only: if to only get the stats of available members
        :return: a `UserMessageStats` containing the processed data
        """
        return MessageStatsDataProcessor._get_user_msg_stats(
            MessageRecordStatisticsManager.get_user_messages_by_category(
                chcoll_data.child_channel_oids, hours_within=hours_within, start=start, end=end),
            chcoll_data, available_only=available_only
        )

    @staticmethod
    def get_user_channel_ranking(channel_data: ChannelModel, root_oid: ObjectId, *,
                                 hours_within: Optional[int] = None, start: Optional[datetime] = None,
                                 end: Optional[datetime] = None) \
            -> UserMessageRanking:
        """
        Get the message count ranking of ``root_oid`` in ``channel_data``.

        :param channel_data: channel to get the user message ranking
        :param root_oid: user OID to get the message ranking
        :param hours_within: time range in hours of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: rank of `root_oid` in `channel_data``
        """
        return MessageStatsDataProcessor._get_user_msg_ranking(
            channel_data.id, root_oid, hours_within=hours_within, start=start, end=end)

    @staticmethod
    def get_user_chcoll_ranking(chcoll_data: ChannelCollectionModel, root_oid: ObjectId, *,
                                hours_within: Optional[int] = None, start: Optional[datetime] = None,
                                end: Optional[datetime] = None) \
            -> UserMessageRanking:
        """
        Get the message count ranking of ``root_oid`` in ``chcoll_data``.

        :param chcoll_data: channel collection to get the user message ranking
        :param root_oid: user OID to get the message ranking
        :param hours_within: time range in hours of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :return: rank of `root_oid` in `channel_data``
        """
        return MessageStatsDataProcessor._get_user_msg_ranking(
            chcoll_data.child_channel_oids, root_oid, hours_within=hours_within, start=start, end=end)

    @staticmethod
    def get_recent_messages(channel_data: ChannelModel, limit: Optional[int] = None, tz: Optional[tzinfo] = None) \
            -> HandledMessageRecords:
        """
        Get the most recent messages of ``channel_data``.

        :param channel_data: channel to get the recent messages
        :param limit: maximum count of the messages to be returned
        :param tz: timezone info to apply on the message timestamps
        :return: a `HandledMessageRecords`
        """
        ret = []
        msgs = list(MessageRecordStatisticsManager.get_recent_messages(channel_data.id, limit))
        uids = {msg.user_root_oid for msg in msgs}
        uids_handled = IdentitySearcher.get_batch_user_name(uids, channel_data)

        for msg in msgs:
            ret.append(HandledMessageRecordEntry(model=msg, user_name=uids_handled[msg.user_root_oid], tz=tz))

        return HandledMessageRecords(data=ret)

    @staticmethod
    def get_user_channel_message_count_interval(channel_data: ChannelModel, *,
                                                hours_within: Optional[int] = None, start: Optional[datetime] = None,
                                                end: Optional[datetime] = None, period_count: Optional[int] = None,
                                                tz: Optional[tzinfo] = None, available_only: bool = True) \
            -> UserMessageCountIntervalResult:
        """
        Get the interval user message count stats in ``channel_data``.

        Check the documentation of :class:`MemberMessageCountResult` for more details.

        :param channel_data: channel to get the interval user message stats
        :param hours_within: time range in hours of the data
        :param start: starting timestamp of the data
        :param end: ending timestamp of the data
        :param period_count: count of the periods/interval to get the data
        :param tz: timezone info to apply for interval separation
        :param available_only: if to get the stats of available members only
        :return: a `UserMessageCountIntervalResult`
        """
        data = MessageRecordStatisticsManager.get_user_messages_total_count(
            channel_data.id, hours_within=hours_within, start=start, end=end,
            period_count=period_count or 3, tzinfo_=tz)

        uname_dict = IdentitySearcher.get_batch_user_name(
            ProfileManager.get_channel_member_oids(channel_data.id, available_only=available_only), channel_data)

        return UserMessageCountIntervalResult(
            original_result=data, uname_dict=uname_dict, available_only=available_only)


# region Dataclasses for `BotUsageStatsDataProcessor`


@dataclass
class PerMemberStatsEntry:
    """Entry for :class:`PerMemberStats`."""

    user_name: str
    data_points: List[int]
    data_sum: int


@dataclass
class PerMemberStats:
    """Collection of :class:`PerMemberStatsEntry`."""

    data: List[PerMemberStatsEntry]
    features: List[BotFeature]


# endregion


class BotUsageStatsDataProcessor:
    """Class to integrate the operations of getting the bot usage stats and process them for webpage rendering."""

    # pylint: disable=too-few-public-methods

    @staticmethod
    def get_per_user_bot_usage(channel_data: ChannelModel, *, hours_within: Optional[int] = None) \
            -> PerMemberStats:
        """
        Get user bot usage stats in ``channel_data``.

        :param channel_data: channel to get the bot usage stats
        :param hours_within: time range in hours of the data
        :return: a `PerMemberStats`
        """
        data = []
        features = list(BotFeature)

        members = ProfileManager.get_channel_prof_conn(channel_data.id, available_only=True)

        usage_data = BotFeatureUsageDataManager.get_channel_per_user_usage(
            channel_data.id, hours_within=hours_within, member_oid_list=[d.user_oid for d in members]).data
        uid_handled = IdentitySearcher.get_batch_user_name(usage_data, channel_data)

        for uid, name in uid_handled.items():
            usage_dict = usage_data[uid]

            data.append(
                PerMemberStatsEntry(
                    user_name=name, data_points=[usage_dict.get(ft, 0) for ft in features],
                    data_sum=sum(usage_dict.values())
                )
            )

        return PerMemberStats(data=data, features=features)

    # pylint: enable=too-few-public-methods
