from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set, Dict, Iterable, Union

import pytz
from bson import ObjectId

from extutils.emailutils import MailSender
from models import ChannelModel, ChannelCollectionModel
from mongodb.factory import ChannelManager, MessageRecordStatisticsManager, RootUserManager, ProfileManager

__all__ = ("IdentitySearcher",)


@dataclass
class ChannelData:
    channel_model: ChannelModel
    channel_name: str


class IdentitySearcher:
    @staticmethod
    def search_channel(keyword: str, root_oid: ObjectId) -> List[ChannelData]:
        """
        Search the channels that the user ``root_oid`` is inside using ``keyword``.

        This search **hides** all private channels.

        Returned result will be sorted by last message time (DESC) then by its ID (DESC).

        -----------

        ``keyword`` can be:

        - partial word from the message of a channel

        - a part of the default name of a channel

        - a part of the token of a channel

        if ``keyword`` is an empty string, the method will list all channels that the users is inside and not hidden.

        :param keyword: keyword to search the channel
        :param root_oid: OID of the user inside the returned channels
        :return: list of `ChannelData` that the user is in and match the conditions
        """
        checked_choid: Set[ObjectId] = set()  # This prevents duplicated entries
        ret: List[ChannelData] = []
        missing = []

        # Get channels that the user is in - early terminate if not in any channel
        ch_oids = ProfileManager.get_users_exist_channel_dict([root_oid]).get(root_oid)
        if not ch_oids:
            return ret

        # Get channels by default name
        for ch_model in ChannelManager.get_channel_default_name(keyword, hide_private=True):
            ch_oid = ch_model.id

            if ch_oid not in ch_oids:
                continue

            checked_choid.add(ch_oid)
            ret.append(ChannelData(ch_model, ch_model.get_channel_name(root_oid)))

        # Get channels by messages
        for channel_oid in MessageRecordStatisticsManager.get_messages_distinct_channel(keyword):
            if channel_oid in checked_choid or channel_oid not in ch_oids:
                continue

            checked_choid.add(channel_oid)
            ch_model = ChannelManager.get_channel_oid(channel_oid, hide_private=True)

            if ch_model:
                ret.append(ChannelData(ch_model, ch_model.get_channel_name(root_oid)))
            else:
                missing.append(channel_oid)

        # Send email report if hanging channel OID found in messages
        if missing:
            MailSender.send_email_async(
                f"Channel OID have no corresponding channel data in message record.\n"
                f"{' | '.join([str(i) for i in missing])}",
                subject="Missing Channel Data")

        # Sort the resulting list
        last_msg_dict = MessageRecordStatisticsManager.get_channel_last_message_ts(root_oid, list(checked_choid))

        def sort_key(data):
            cid = data.channel_model.id

            return last_msg_dict.get(cid, datetime.min.replace(tzinfo=pytz.utc)), cid

        return list(sorted(ret, key=sort_key, reverse=True))

    @staticmethod
    def get_batch_user_name(user_oids: Iterable[ObjectId], channel_data: Union[ChannelModel, ChannelCollectionModel],
                            *, on_not_found: Optional[str] = None) -> Dict[ObjectId, str]:
        ret = {}

        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="GetUserNames") as executor:
            futures = []
            for uid in user_oids:
                futures.append(executor.submit(RootUserManager.get_root_data_uname, uid, channel_data, on_not_found))

            for completed in futures:
                if result := completed.result():
                    ret[result.user_id] = result.user_name

        return ret
