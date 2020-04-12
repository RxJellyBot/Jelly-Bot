import math
from collections import namedtuple
from dataclasses import dataclass, field, InitVar
from datetime import tzinfo, datetime
from typing import List, Optional, Union, NamedTuple, Dict, Tuple, Iterator

from bson import ObjectId

from extutils.dt import now_utc_aware, localtime
from extutils.utils import enumerate_ranking
from flags import BotFeature, MessageType
from models import (
    ChannelModel, ChannelCollectionModel, MessageRecordModel,
    MemberMessageByCategoryResult, MemberMessageCountResult
)
from mongodb.factory import (
    MessageRecordStatisticsManager, ProfileManager, BotFeatureUsageDataManager
)
from .search import IdentitySearcher


# region Dataclasses for `MessageStatsDataProcessor`
@dataclass
class UserMessageStatsEntry:
    user_oid: ObjectId
    user_name: str
    available: bool
    total_count: int
    total_count_ratio: float
    category_count: List[NamedTuple]
    rank: int = field(default=1, init=False)

    @property
    def ratio_pct_str(self) -> str:
        return f"{self.total_count_ratio:.02%}"

    def set_rank(self, rank: int):
        self.rank = rank


@dataclass
class UserMessageStats:
    org_stats: InitVar[List[UserMessageStatsEntry]]
    member_stats: List[UserMessageStatsEntry] = field(init=False)
    msg_count: int
    label_category: List[MessageType]

    def __post_init__(self, org_stats: List[UserMessageStatsEntry]):
        self.member_stats = []
        # Disabling T-prefix for datatable sorting in the webpage
        for rank, data in enumerate_ranking(
                list(sorted(org_stats, key=lambda x: x.total_count, reverse=True)),
                is_equal=lambda cur, prv: cur.total_count == prv.total_count,
                t_prefix=False):
            data.set_rank(rank)
            self.member_stats.append(data)


@dataclass
class UserMessageRanking:
    rank: int
    total: int

    @property
    def available(self) -> bool:
        return self.rank > -1

    def __str__(self):
        return f"#{self.rank} / #{self.total}"


@dataclass
class HandledMessageRecordEntry:
    model: MessageRecordModel
    user_name: str
    timestamp: str = field(init=False)
    content_type: MessageType = field(init=False)
    content_html: str = field(init=False)
    process_time_ms: float = field(init=False)

    tz: InitVar[Optional[tzinfo]]

    def __post_init__(self, tz: Optional[tzinfo]):
        self.timestamp = localtime(ObjectId(self.model.id).generation_time, tz).strftime("%Y-%m-%d %H:%M:%S")
        self.content_type = self.model.message_type
        self.content_html = self.model.message_content.replace("\n", "<br>")
        self.process_time_ms = self.model.process_time_secs * 1000


@dataclass
class HandledMessagesComposition:
    label_type: List[MessageType] = field(init=False, default_factory=list)
    label_count: List[int] = field(init=False, default_factory=list)

    counter_obj: InitVar[Dict[MessageType, int]]

    def __post_init__(self, counter_obj: Dict[MessageType, int]):
        for cat, count in counter_obj.items():
            self.label_type.append(cat.key)
            self.label_count.append(count)


@dataclass
class HandledMessageRecords:
    data: List[HandledMessageRecordEntry]
    avg_processing_secs: Dict[MessageType, float] = field(init=False, default_factory=dict)
    message_frequency = float
    unique_sender_count: int = field(init=False, default_factory=int)
    msg_composition: HandledMessagesComposition = field(init=False, default=HandledMessagesComposition({}))

    def __post_init__(self):
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
    member_name: str
    available: bool
    count_list: List[int]
    rank_list: List[str]
    count_total: int = field(init=False)

    def __post_init__(self):
        self.count_total = sum(self.count_list)

    @property
    def rank_count_zip(self):
        return zip(self.rank_list, self.count_list)


@dataclass
class UserDailyMessageResult:
    label_dates: List[str]
    active_members: List[int]
    entries: List[UserDailyMessageEntry]

    @property
    def label_dates_jsarr(self):
        return f"[{self.label_dates}]"


@dataclass
class UserMessageCountIntervalEntry:
    user_name: str
    total: int
    count: InitVar[List[int]]
    count_data: Iterator[Tuple[int, int, float]] = field(init=False)
    increases: int = 0
    decreases: int = 0
    avg_diff: float = field(init=False)
    avg_diff_nrm: float = field(init=False)
    avg_diff_pct: float = field(init=False)

    def __post_init__(self, count: List[int]):
        # Reverse to put the most recent at the front
        difference = []
        difference_pct = []
        count = list(reversed(count))

        for idx in range(len(count)):
            base = count[0]
            data = count[idx]

            diff = base - data
            difference.append(diff)
            difference_pct.append(diff / data * 100 if data != 0 else (math.inf if diff != 0 else 0))

            if diff > 0:
                self.increases += 1
            elif diff < 0:
                self.decreases += 1

        self.count_data = zip(count, difference, difference_pct)
        if len(difference) == 1:
            self.avg_diff = sum(difference)
            self.avg_diff_pct = sum(filter(lambda x: not math.isinf(x), difference_pct))
        else:
            self.avg_diff = sum(difference) / (len(difference) - 1)
            self.avg_diff_pct = sum(filter(lambda x: not math.isinf(x), difference_pct)) / (len(difference_pct) - 1)

        if self.avg_diff_pct == 0 and self.avg_diff > 0:
            self.avg_diff_pct = math.inf
            self.avg_diff_nrm = self.avg_diff
        elif self.avg_diff_pct != 0:
            self.avg_diff_nrm = self.avg_diff / abs(self.avg_diff_pct / 100)
        else:
            self.avg_diff_nrm = 0


@dataclass
class UserMessageCountIntervalResult:
    original_result: InitVar[MemberMessageCountResult]
    uname_dict: InitVar[Dict[ObjectId, str]]
    available_only: InitVar[bool]
    time_ranges: List[str] = field(init=False)
    data: List[UserMessageCountIntervalEntry] = field(init=False)
    is_inf: bool = field(init=False)

    def __post_init__(
            self, original_result: MemberMessageCountResult, uname_dict: Dict[ObjectId, str], available_only: bool):
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
                self.data.append(UserMessageCountIntervalEntry(
                    user_name=name, total=0, count=[0] * original_result.interval))


# endregion


class MessageStatsDataProcessor:
    @staticmethod
    def _get_user_msg_stats_(msg_result: MemberMessageByCategoryResult,
                             ch_data: Union[ChannelModel, ChannelCollectionModel] = None,
                             available_only: bool = True) -> UserMessageStats:
        entries: List[UserMessageStatsEntry] = []

        if isinstance(ch_data, ChannelModel):
            ch_oids = [ch_data.id]
        elif isinstance(ch_data, ChannelCollectionModel):
            ch_oids = ch_data.child_channel_oids
        else:
            raise ValueError(f"The type of `ch_data` must either be `ChannelModel` or `ChannelCollectionModel`. "
                             f"({type(ch_data)})")

        msg_rec_d = {uid: d for uid, d in msg_result.data.items()}
        msg_rec = {}
        available_dict = {}
        for member in ProfileManager.get_channel_members(ch_oids, available_only=available_only):
            msg_rec[member.user_oid] = msg_rec_d.get(member.user_oid, msg_result.get_default_data_entry())
            available_dict[member.user_oid] = member.available

        if msg_rec:
            individual_msgs = [vals.total for vals in msg_rec.values()]
            max_individual_msg: int = max(individual_msgs)

            uid_handled = IdentitySearcher.get_batch_user_name(
                msg_rec.keys(), ch_data, on_not_found="(N/A)")

            for uid, name in uid_handled.items():
                data_cat = msg_rec[uid]

                sum_ = data_cat.total

                cat_count = []
                CategoryEntry = namedtuple("CategoryEntry", ["count", "percentage"])
                for cat in msg_result.label_category:
                    ct = data_cat.get_count(cat)
                    cat_count.append(CategoryEntry(count=ct, percentage=ct / sum_ * 100 if sum_ > 0 else 0))

                entries.append(
                    UserMessageStatsEntry(
                        user_oid=uid, user_name=name, category_count=cat_count, available=available_dict[uid],
                        total_count=sum_, total_count_ratio=sum_ / max_individual_msg if max_individual_msg > 0 else 0)
                )

            return UserMessageStats(
                org_stats=entries, msg_count=sum(individual_msgs), label_category=msg_result.label_category)
        else:
            return UserMessageStats(
                org_stats=[], msg_count=0, label_category=msg_result.label_category)

    @staticmethod
    def _get_user_msg_ranking_(
            channel_oids: Union[List[ObjectId], ObjectId], root_oid: ObjectId, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None):
        data = sorted(
            MessageRecordStatisticsManager.get_user_messages_by_category(
                channel_oids, hours_within=hours_within, start=start, end=end).data.items(),
            key=lambda _: _[1].total, reverse=True)
        for idx, item in enumerate(data, start=1):
            oid, entry = item
            if oid == root_oid:
                return UserMessageRanking(rank=idx, total=len(data))

        return UserMessageRanking(rank=-1, total=len(data))

    @staticmethod
    def get_user_daily_message(
            channel_data: ChannelModel, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None,
            tz: Optional[tzinfo] = None, available_only: Optional[bool] = True) \
            -> UserDailyMessageResult:
        available_dict = {d.user_oid: d.available
                          for d in ProfileManager.get_channel_members(channel_data.id, available_only=available_only)}
        uname_dict = IdentitySearcher.get_batch_user_name(
            list(available_dict.keys()),
            channel_data, on_not_found="(N/A)")
        result = MessageRecordStatisticsManager.member_daily_message_count(
            channel_data.id, hours_within=hours_within, start=start, end=end, tzinfo_=tz)

        # Array for storing active member count
        actv_mbr = []

        # Create empty arrays for the result
        # Each entry corresponds to daily message count in a specific date
        # Ordered by the date
        proc_count = {}
        proc_rank = {}
        for oid in uname_dict.keys():
            proc_count[oid] = []
            proc_rank[oid] = []

        for date in result.dates:
            # Get the data of the corresponding date
            data_of_date = result.data_count[date]

            # Storing active member count
            actv_mbr.append(len(data_of_date))

            # Get and sort the daily message count
            collated_count = {oid: data_of_date.get(oid, 0) for oid in proc_count.keys()}
            sorted_count = list(sorted(collated_count.items(), key=lambda x: x[1], reverse=True))

            # Insert daily count and rank
            for rank, entry in enumerate_ranking(sorted_count, is_equal=lambda cur, prv: cur[1] == prv[1]):
                uid, count = entry
                proc_count[uid].append(count)
                proc_rank[uid].append(rank)

        entries = [
            UserDailyMessageEntry(
                member_name=name, count_list=proc_count[oid], rank_list=proc_rank[oid], available=available_dict[oid])
            for oid, name in uname_dict.items()]

        return UserDailyMessageResult(label_dates=result.dates, entries=entries, active_members=actv_mbr)

    @staticmethod
    def get_user_channel_messages(
            channel_data: ChannelModel, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None,
            available_only: bool = True) \
            -> UserMessageStats:
        return MessageStatsDataProcessor._get_user_msg_stats_(
            MessageRecordStatisticsManager.get_user_messages_by_category(
                channel_data.id, hours_within=hours_within, start=start, end=end),
            channel_data, available_only
        )

    @staticmethod
    def get_user_chcoll_messages(
            chcoll_data: ChannelCollectionModel, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None,
            available_only: bool = True) \
            -> UserMessageStats:
        return MessageStatsDataProcessor._get_user_msg_stats_(
            MessageRecordStatisticsManager.get_user_messages_by_category(
                chcoll_data.child_channel_oids, hours_within=hours_within, start=start, end=end),
            chcoll_data, available_only=available_only
        )

    @staticmethod
    def get_user_channel_ranking(
            channel_data: ChannelModel, root_oid: ObjectId, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> UserMessageRanking:
        return MessageStatsDataProcessor._get_user_msg_ranking_(
            channel_data.id, root_oid, hours_within=hours_within, start=start, end=end)

    @staticmethod
    def get_user_chcoll_ranking(
            chcoll_data: ChannelCollectionModel, root_oid: ObjectId, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None) \
            -> UserMessageRanking:
        return MessageStatsDataProcessor._get_user_msg_ranking_(
            chcoll_data.child_channel_oids, root_oid, hours_within=hours_within, start=start, end=end)

    @staticmethod
    def get_recent_messages(
            channel_data: ChannelModel, limit: Optional[int] = None, tz: Optional[tzinfo] = None) \
            -> HandledMessageRecords:
        ret = []
        msgs = list(MessageRecordStatisticsManager.get_recent_messages(channel_data.id, limit))
        uids = {msg.user_root_oid for msg in msgs}
        uids_handled = IdentitySearcher.get_batch_user_name(uids, channel_data)

        for msg in msgs:
            ret.append(HandledMessageRecordEntry(model=msg, user_name=uids_handled[msg.user_root_oid], tz=tz))

        return HandledMessageRecords(data=ret)

    @staticmethod
    def get_user_channel_message_count_interval(
            channel_data: ChannelModel, *,
            hours_within: Optional[int] = None, start: Optional[datetime] = None, end: Optional[datetime] = None,
            period_count: Optional[int] = None, tz: Optional[tzinfo] = None,
            available_only: bool = True) -> UserMessageCountIntervalResult:
        data = MessageRecordStatisticsManager.get_user_messages_total_count(
            channel_data.id, hours_within=hours_within, start=start, end=end, period_count=period_count, tzinfo_=tz)

        uname_dict = IdentitySearcher.get_batch_user_name(
            ProfileManager.get_channel_member_oids(channel_data.id, available_only=available_only), channel_data)

        return UserMessageCountIntervalResult(
            original_result=data, uname_dict=uname_dict, available_only=available_only)


# region Dataclasses for `BotUsageStatsDataProcessor`
@dataclass
class PerMemberStatsEntry:
    user_name: str
    data_points: List[int]
    data_sum: int


@dataclass
class PerMemberStats:
    data: List[PerMemberStatsEntry]
    features: List[BotFeature]


# endregion


class BotUsageStatsDataProcessor:
    @staticmethod
    def get_per_user_bot_usage(
            channel_data: ChannelModel, *, hours_within: Optional[int] = None) \
            -> PerMemberStats:
        data = []
        features = [f for f in BotFeature]

        members = ProfileManager.get_channel_members(channel_data.id, available_only=True)

        usage_data = BotFeatureUsageDataManager.get_channel_per_user_usage(
            channel_data.id, hours_within=hours_within, member_oid_list=[d.user_oid for d in members]).data
        uid_handled = IdentitySearcher.get_batch_user_name(usage_data.keys(), channel_data)

        for uid, name in uid_handled.items():
            usage_dict = usage_data[uid]

            data.append(
                PerMemberStatsEntry(
                    user_name=name, data_points=[usage_dict.get(ft, 0) for ft in features],
                    data_sum=sum(usage_dict.values()))
            )

        return PerMemberStats(data=data, features=features)
