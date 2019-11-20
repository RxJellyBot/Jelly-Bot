from dataclasses import dataclass
from typing import List

from bson import ObjectId

from extutils.emailutils import MailSender
from models import ChannelModel
from mongodb.factory import ChannelManager


@dataclass
class CollatedChannelData:
    channel_name: str
    channel_data: ChannelModel


class InfoProcessor:
    @staticmethod
    def collate_child_channel_data(root_oid: ObjectId, child_channel_oids: List[ObjectId]) -> List[CollatedChannelData]:
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
