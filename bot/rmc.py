from dataclasses import dataclass, field
from datetime import datetime, timedelta, tzinfo
from typing import Optional

from bson import ObjectId

from extutils.dt import localtime, now_utc_aware
from JellyBot.systemconfig import Bot
from models import ChannelModel
from mongodb.factory import ChannelManager

__all__ = ["RemoteControl"]


@dataclass
class RemoteControlEntry:
    expiry: datetime = field(init=False)
    tzinfo: tzinfo
    target_channel_oid: ObjectId

    def __post_init__(self):
        self.refresh_expiry()

    def refresh_expiry(self):
        self.expiry = \
            localtime(now_utc_aware(), self.tzinfo) + timedelta(seconds=Bot.RemoteControl.IdleDeactivateSeconds)

    @property
    def target_channel(self) -> Optional[ChannelModel]:
        return ChannelManager.get_channel_oid(self.target_channel_oid)

    @property
    def expiry_str(self) -> str:
        return self.expiry.strftime("%Y-%m-%d %H:%M:%S (UTC%Z)")


class RemoteControl:
    _core_ = {}

    @classmethod
    def activate(
            cls, user_oid: ObjectId, source_channel_oid: ObjectId, target_channel_oid: ObjectId,
            tzinfo_: Optional[tzinfo] = None) -> RemoteControlEntry:
        """Activate the remote control and return the created entry in the holder."""
        entry = RemoteControlEntry(target_channel_oid=target_channel_oid, tzinfo=tzinfo_)
        cls._core_[RemoteControl._mix_key_(user_oid, source_channel_oid)] = entry
        return entry

    @classmethod
    def deactivate(cls, user_oid: ObjectId, source_channel_oid: ObjectId):
        del cls._core_[RemoteControl._mix_key_(user_oid, source_channel_oid)]

    @classmethod
    def get_current(cls, user_oid: ObjectId, source_channel_oid: ObjectId,
                    *, update_expiry: bool = True) -> Optional[RemoteControlEntry]:
        """
        Get the current activating remote control.
        If available, update the expiry time. Otherwise, return `None`.
        """
        ret = cls._core_.get(RemoteControl._mix_key_(user_oid, source_channel_oid))
        if not ret:
            return None

        if now_utc_aware() > ret.expiry:
            del cls._core_[RemoteControl._mix_key_(user_oid, source_channel_oid)]
            return None
        else:
            if update_expiry:
                ret.refresh_expiry()
            return ret

    @staticmethod
    def _mix_key_(user_oid: ObjectId, source_channel_oid: ObjectId):
        return user_oid, source_channel_oid
