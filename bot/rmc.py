from dataclasses import dataclass, field
from datetime import datetime, timedelta, tzinfo
from typing import Optional

from bson import ObjectId

from extutils.dt import localtime, now_utc_aware
from JellyBot.systemconfig import Bot
from models import ChannelModel, RootUserModel
from mongodb.factory import ChannelManager

__all__ = ["RemoteControl"]


@dataclass
class RemoteControlEntry:
    expiry: datetime = field(init=False)
    tzinfo: tzinfo
    target_channel: ChannelModel

    def __post_init__(self):
        self.refresh_expiry()

    def refresh_expiry(self):
        self.expiry = \
            localtime(now_utc_aware(), self.tzinfo) + timedelta(seconds=Bot.RemoteControl.IdleDeactivateSeconds)

    @property
    def expiry_str(self) -> str:
        return self.expiry.strftime("%Y-%m-%d %H:%M:%S (UTC%Z)")


class RemoteControl:
    _core_ = {}

    @classmethod
    def activate(cls, root_model: RootUserModel, source_channel_oid: ObjectId, target_channel_oid: ObjectId) -> bool:
        target = ChannelManager.get_channel_oid(target_channel_oid)

        if not target:
            return False

        cls._core_[RemoteControl.mix_key(root_model.id, source_channel_oid)] = \
            RemoteControlEntry(target_channel=target, tzinfo=root_model.config.tzinfo)

        return True

    @classmethod
    def deactivate(cls, user_oid: ObjectId, source_channel_oid: ObjectId):
        del cls._core_[RemoteControl.mix_key(user_oid, source_channel_oid)]

    @classmethod
    def get_current(cls, user_oid: ObjectId, source_channel_oid: ObjectId) -> Optional[RemoteControlEntry]:
        ret = cls._core_.get(RemoteControl.mix_key(user_oid, source_channel_oid))
        if ret and now_utc_aware() > ret.expiry:
            del cls._core_[RemoteControl.mix_key(user_oid, source_channel_oid)]
            return None
        else:
            return ret

    @staticmethod
    def mix_key(user_oid: ObjectId, source_channel_oid: ObjectId):
        return user_oid, source_channel_oid
