from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional

from models import ChannelModel
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


class MessageStatsDataProcessor:
    @staticmethod
    def get_user_messages(
            channel_data: ChannelModel, hours_within: Optional[int] = None) \
            -> UserMessageStats:
        entries: List[UserMessageStatsEntry] = []

        msg_rec = MessageRecordStatisticsManager.get_channel_user_messages(channel_data.id, hours_within)

        if msg_rec:
            total: int = sum(msg_rec.values())

            # Obtained from https://stackoverflow.com/a/40687012/11571888
            with ThreadPoolExecutor(max_workers=len(msg_rec), thread_name_prefix="UserNameQuery") as executor:
                futures = []
                for uid, ct in msg_rec.items():
                    futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, channel_data))

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
