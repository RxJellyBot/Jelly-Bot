from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional, Union, NamedTuple

from bson import ObjectId

from flags import BotFeature, MessageType
from models import ChannelModel, ChannelCollectionModel, OID_KEY, MemberMessageResult
from mongodb.factory import RootUserManager, MessageRecordStatisticsManager, ProfileManager, BotFeatureUsageDataManager


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

            # Obtained from https://stackoverflow.com/a/40687012/11571888
            # Workers cannot be too big as it will suck out the connections of MongoDB Atlas
            # However, it also cannot be too small as this heavily impact the performance
            with ThreadPoolExecutor(max_workers=10, thread_name_prefix="UserNameQuery") as executor:
                futures = []
                for uid in msg_rec.keys():
                    futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, ch_data))

                # Non-lock call & Free resources when execution is done
                executor.shutdown(False)

                for completed in futures:
                    result = completed.result()
                    data_cat = msg_rec[result.user_id]

                    sum_ = sum(data_cat.values())

                    cat_count = []
                    CategoryEntry = namedtuple("CategoryEntry", ["count", "percentage"])
                    for cat in msg_result.label_category:
                        ct = data_cat.get(cat, 0)
                        cat_count.append(CategoryEntry(count=ct, percentage=ct / sum_ * 100 if sum_ > 0 else 0))

                    entries.append(
                        UserMessageStatsEntry(
                            user_name=result.user_name, category_count=cat_count,
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

        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="BotUsage") as executor:
            futures = []
            for uid in usage_data.keys():
                futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, channel_data))

            # Non-lock call & Free resources when execution is done
            executor.shutdown(False)

            for completed in futures:
                result = completed.result()
                usage_dict = usage_data[result.user_id]

                data.append(
                    PerMemberStatsEntry(
                        user_name=result.user_name, data_points=[usage_dict.get(ft, 0) for ft in features],
                        data_sum=sum(usage_dict.values()))
                )

        return PerMemberStats(data=data, features=features)
