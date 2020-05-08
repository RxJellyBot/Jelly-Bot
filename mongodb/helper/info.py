from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from extutils.dt import localtime
from extutils.emailutils import MailSender
from models import ChannelModel
from mongodb.factory import ChannelManager, ProfileManager, MessageRecordStatisticsManager
from mongodb.helper import IdentitySearcher


@dataclass
class CollatedChannelData:
    channel_name: str
    channel_data: ChannelModel


@dataclass
class MemberInfoEntry:
    user_oid: ObjectId
    user_name: str
    first_joined: datetime
    last_message_at: Optional[datetime] = None

    @property
    def first_joined_str(self):
        return self.first_joined.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def last_message_at_str(self):
        return self.last_message_at.strftime("%Y-%m-%d %H:%M:%S")


class InfoProcessor:
    @staticmethod
    def collate_child_channel_data(root_oid: ObjectId, child_channel_oids: List[ObjectId]) \
            -> List[CollatedChannelData]:
        accessible: List[CollatedChannelData] = []
        inaccessible: List[CollatedChannelData] = []

        missing_oids = []

        for ccoid in child_channel_oids:
            cdata = ChannelManager.get_channel_oid(ccoid)

            if cdata:
                ccd = CollatedChannelData(channel_name=cdata.get_channel_name(root_oid), channel_data=cdata)

                if cdata.bot_accessible:
                    accessible.append(ccd)
                else:
                    inaccessible.append(ccd)
            else:
                missing_oids.append(ccoid)

        if missing_oids:
            MailSender.send_email_async(f"No associated channel data found of the channel IDs below:<br>"
                                        f"<pre>{' / '.join([str(oid) for oid in missing_oids])}</pre>")

        accessible = sorted(accessible, key=lambda data: data.channel_data.id, reverse=True)
        inaccessible = sorted(inaccessible, key=lambda data: data.channel_data.id, reverse=True)

        return accessible + inaccessible

    @staticmethod
    def get_member_info(channel_model: ChannelModel) -> List[MemberInfoEntry]:
        ret = []

        prof_conns = ProfileManager.get_channel_members(channel_model.id, available_only=True)
        user_oids = [mdl.user_oid for mdl in prof_conns]

        user_name_dict = IdentitySearcher.get_batch_user_name(user_oids, channel_model)
        last_message_oids = MessageRecordStatisticsManager.get_user_last_message_ts(channel_model.id, user_oids)

        for prof_conn in prof_conns:
            user_oid = prof_conn.user_oid
            user_name = user_name_dict.get(user_oid) or str(user_oid)
            first_joined = localtime(prof_conn.id.generation_time)
            last_message_at = last_message_oids.get(user_oid)
            if last_message_at:
                last_message_at = localtime(last_message_at)

            ret.append(MemberInfoEntry(
                user_oid=user_oid, user_name=user_name, first_joined=first_joined, last_message_at=last_message_at))

        return ret
