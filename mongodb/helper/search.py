from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional, Set, Dict, Iterable

from bson import ObjectId

from extutils.emailutils import MailSender
from models import ChannelModel
from mongodb.factory import ChannelManager, MessageRecordStatisticsManager, RootUserManager


@dataclass
class ChannelData:
    channel_model: ChannelModel
    channel_name: str


class IdentitySearcher:
    @staticmethod
    def search_channel(keyword: str, root_oid: Optional[ObjectId] = None) -> List[ChannelData]:
        """The keyword could be
        - A piece of the message comes from a channel
        - The name of the channel"""
        checked_choid: Set[ObjectId] = set()
        ret: List[ChannelData] = []
        missing = []

        for ch_model in ChannelManager.get_channel_default_name(keyword, hide_private=True):
            checked_choid.add(ch_model.id)
            ret.append(ChannelData(ch_model, ch_model.get_channel_name(root_oid)))

        for channel_oid in MessageRecordStatisticsManager.get_messages_distinct_channel(keyword):
            if channel_oid not in checked_choid:
                checked_choid.add(channel_oid)
                ch_model = ChannelManager.get_channel_oid(channel_oid, hide_private=True)

                if ch_model:
                    ret.append(ChannelData(ch_model, ch_model.get_channel_name(root_oid)))
                else:
                    missing.append(channel_oid)

        if missing:
            MailSender.send_email_async(
                f"Channel OID have no corresponding channel data in message record.\n"
                f"{' | '.join([str(i) for i in missing])}",
                subject="Missing Channel Data")

        return ret

    @staticmethod
    def get_batch_user_name(user_oids: Iterable[ObjectId], channel_data: ChannelModel,
                            on_not_found: Optional[str] = None) -> Dict[ObjectId, str]:
        ret = {}

        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="GetUserNames") as executor:
            futures = []
            for uid in user_oids:
                futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, channel_data, on_not_found))

            # Non-lock call & Free resources when execution is done
            executor.shutdown(False)

            for completed in futures:
                result = completed.result()
                ret[result.user_id] = result.user_name

        return ret
