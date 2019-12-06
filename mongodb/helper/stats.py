from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional, Union

from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from models import ChannelModel, ChannelCollectionModel, OID_KEY
from mongodb.factory import RootUserManager, MessageRecordStatisticsManager


@dataclass
class UserMessageStatsEntry:
    user_name: str
    message_count: int
    message_percentage: float

    @property
    def percent_str(self) -> str:
        return f"{self.message_percentage:.02%}"


@dataclass
class UserMessageStats:
    member_stats: List[UserMessageStatsEntry]
    msg_count: int

    def __post_init__(self):
        self.member_stats = list(sorted(self.member_stats, key=lambda x: x.message_count, reverse=True))


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
    def _get_user_msg_stats_(msg_rec: CommandCursor, ch_data: ChannelModel = None) -> UserMessageStats:
        entries: List[UserMessageStatsEntry] = []

        msg_rec = {d[OID_KEY]: d["count"] for d in list(msg_rec)}

        if msg_rec:
            total: int = sum(msg_rec.values())

            # Obtained from https://stackoverflow.com/a/40687012/11571888
            # Workers cannot be too big as it will suck out the connections of MongoDB Atlas
            # However, it also cannot be too small as this heavily impact the performance
            with ThreadPoolExecutor(max_workers=10, thread_name_prefix="UserNameQuery") as executor:
                futures = []
                for uid, ct in msg_rec.items():
                    futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, ch_data))

                # Non-lock call & Free resources when execution is done
                executor.shutdown(False)

                for completed in futures:
                    result = completed.result()
                    count = msg_rec[result.user_id]

                    entries.append(
                        UserMessageStatsEntry(
                            user_name=result.user_name, message_count=count, message_percentage=count / total)
                    )

            return UserMessageStats(member_stats=entries, msg_count=total)
        else:
            return UserMessageStats(member_stats=[], msg_count=0)

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
