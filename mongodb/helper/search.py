from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional, Set, Dict, Iterable, Union

from bson import ObjectId

from extutils.emailutils import MailSender
from models import ChannelModel, ChannelCollectionModel
from mongodb.factory import ChannelManager, MessageRecordStatisticsManager, RootUserManager


@dataclass
class ChannelData:
    channel_model: ChannelModel
    channel_name: str


class IdentitySearcher:
    @staticmethod
    def search_channel(keyword: str, root_oid: ObjectId) -> List[ChannelData]:
        """
        Search the channels that the user ``root_oid`` is inside using ``keyword``.

        ``keyword`` can be:

        - partial word from the message of a channel

        - a part of the default name of a channel

        - a part of the token of a channel

        :param keyword: keyword to search the channel
        :param root_oid: OID of the user inside the returned channels
        :return: list of `ChannelData` that the user is in and match the conditions
        """
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
    def get_batch_user_name(user_oids: Iterable[ObjectId], channel_data: Union[ChannelModel, ChannelCollectionModel],
                            on_not_found: Optional[str] = None) -> Dict[ObjectId, str]:
        ret = {}

        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="GetUserNames") as executor:
            futures = []
            for uid in user_oids:
                futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, channel_data, on_not_found))

            for completed in futures:
                result = completed.result()
                ret[result.user_id] = result.user_name

        return ret
