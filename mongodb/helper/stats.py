from collections import namedtuple
from dataclasses import dataclass, field, InitVar
from typing import List, Optional, Union, NamedTuple, Dict

from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import BotFeature, MessageType
from models import ChannelModel, ChannelCollectionModel, OID_KEY, MemberMessageResult, MessageRecordModel
from mongodb.factory import (
    MessageRecordStatisticsManager, ProfileManager, BotFeatureUsageDataManager
)

from .search import IdentitySearcher


@dataclass
class UserMessageStatsEntry:
    user_name: str
    total_count: int
    total_count_ratio: float
    category_count: List[NamedTuple]

    @property
    def ratio_pct_str(self) -> str:
        return f"{self.total_count_ratio:.02%}"


@dataclass
class UserMessageStats:
    member_stats: List[UserMessageStatsEntry]
    msg_count: int
    label_category: List[MessageType]

    def __post_init__(self):
        self.member_stats = list(sorted(self.member_stats, key=lambda x: x.total_count, reverse=True))


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

    def __post_init__(self):
        self.timestamp = ObjectId(self.model.id).generation_time.strftime("%Y-%m-%d %H:%M:%S")
        self.content_type = self.model.message_type
        self.content_html = self.model.message_content.replace("\n", "<br>")


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


class MessageStatsDataProcessor:
    @staticmethod
    def _get_user_msg_stats_(msg_result: MemberMessageResult, ch_data: ChannelModel = None) -> UserMessageStats:
        entries: List[UserMessageStatsEntry] = []

        msg_rec_d = {uid: d for uid, d in msg_result.data.items()}
        msg_rec = {}
        for member in ProfileManager.get_channel_members(ch_data.id, available_only=True):
            msg_rec[member.user_oid] = msg_rec_d.get(member.user_oid, msg_result.get_default_data_entry())

        if msg_rec:
            individual_msgs = [sum(vals.values()) for vals in msg_rec.values()]
            max_individual_msg: int = max(individual_msgs)

            uid_handled = IdentitySearcher.get_batch_user_name(msg_rec.keys(), ch_data)

            for uid, name in uid_handled.items():
                data_cat = msg_rec[uid]

                sum_ = sum(data_cat.values())

                cat_count = []
                CategoryEntry = namedtuple("CategoryEntry", ["count", "percentage"])
                for cat in msg_result.label_category:
                    ct = data_cat.get(cat, 0)
                    cat_count.append(CategoryEntry(count=ct, percentage=ct / sum_ * 100 if sum_ > 0 else 0))

                entries.append(
                    UserMessageStatsEntry(
                        user_name=name, category_count=cat_count,
                        total_count=sum_, total_count_ratio=sum_ / max_individual_msg if max_individual_msg > 0 else 0)
                )

            return UserMessageStats(
                member_stats=entries, msg_count=sum(individual_msgs), label_category=msg_result.label_category)
        else:
            return UserMessageStats(
                member_stats=[], msg_count=0, label_category=msg_result.label_category)

    @staticmethod
    def _get_user_msg_ranking_(
            channel_oids: Union[List[ObjectId], ObjectId], root_oid: ObjectId, hours_within: Optional[int] = None):
        data = list(MessageRecordStatisticsManager.get_user_messages(channel_oids, hours_within))
        for idx, entry in enumerate(data, start=1):
            if entry[OID_KEY] == root_oid:
                return UserMessageRanking(rank=idx, total=len(data))

        return UserMessageRanking(rank=-1, total=len(data))

    @staticmethod
    def get_user_channel_messages(
            channel_data: ChannelModel, hours_within: Optional[int] = None) \
            -> UserMessageStats:
        return MessageStatsDataProcessor._get_user_msg_stats_(
            MessageRecordStatisticsManager.get_user_messages(channel_data.id, hours_within),
            channel_data
        )

    @staticmethod
    def get_user_chcoll_messages(
            chcoll_data: ChannelCollectionModel, hours_within: Optional[int] = None) \
            -> UserMessageStats:
        return MessageStatsDataProcessor._get_user_msg_stats_(
            MessageRecordStatisticsManager.get_user_messages(chcoll_data.child_channel_oids, hours_within))

    @staticmethod
    def get_user_channel_ranking(
            channel_data: ChannelModel, root_oid: ObjectId, hours_within: Optional[int] = None) \
            -> UserMessageRanking:
        return MessageStatsDataProcessor._get_user_msg_ranking_(channel_data.id, root_oid, hours_within)

    @staticmethod
    def get_user_chcoll_ranking(
            chcoll_data: ChannelCollectionModel, root_oid: ObjectId, hours_within: Optional[int] = None) \
            -> UserMessageRanking:
        return MessageStatsDataProcessor._get_user_msg_ranking_(chcoll_data.child_channel_oids, root_oid, hours_within)

    @staticmethod
    def get_recent_messages(channel_data: ChannelModel, limit: Optional[int] = None) -> HandledMessageRecords:
        ret = []
        msgs = list(MessageRecordStatisticsManager.get_recent_messages(channel_data.id, limit))
        uids = {msg.user_root_oid for msg in msgs}
        uids_handled = IdentitySearcher.get_batch_user_name(uids, channel_data)

        for msg in msgs:
            ret.append(HandledMessageRecordEntry(model=msg, user_name=uids_handled[msg.user_root_oid]))

        return HandledMessageRecords(data=ret)


@dataclass
class PerMemberStatsEntry:
    user_name: str
    data_points: List[int]
    data_sum: int


@dataclass
class PerMemberStats:
    data: List[PerMemberStatsEntry]
    features: List[BotFeature]


class BotUsageStatsDataProcessor:
    @staticmethod
    def get_per_user_bot_usage(
            channel_data: ChannelModel, hours_within: Optional[int] = None) \
            -> PerMemberStats:
        data = []
        features = [f for f in BotFeature]

        members = ProfileManager.get_channel_members(channel_data.id, available_only=True)

        usage_data = BotFeatureUsageDataManager.get_channel_per_user_usage(
            channel_data.id, hours_within, [d.user_oid for d in members]).data
        uid_handled = IdentitySearcher.get_batch_user_name(usage_data.keys(), channel_data)

        for uid, name in uid_handled.items():
            usage_dict = usage_data[uid]

            data.append(
                PerMemberStatsEntry(
                    user_name=name, data_points=[usage_dict.get(ft, 0) for ft in features],
                    data_sum=sum(usage_dict.values()))
            )

        return PerMemberStats(data=data, features=features)
