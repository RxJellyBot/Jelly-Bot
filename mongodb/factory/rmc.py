from typing import Optional
from datetime import datetime, timedelta

from bson import ObjectId

from JellyBot.systemconfig import Bot
from extutils.dt import now_utc_aware
from models import RemoteControlEntryModel

from ._base import BaseCollection

__all__ = ["RemoteControlManager"]

DB_NAME = "rmc"


class _RemoteControlManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "data"
    model_class = RemoteControlEntryModel

    def build_indexes(self):
        self.create_index(
            [(RemoteControlEntryModel.UserOid.key, 1),
             (RemoteControlEntryModel.SourceChannelOid.key, 1)],
            name="Entry uniqueness enforcer", unique=True)
        self.create_index(
            RemoteControlEntryModel.ExpiryUtc.key, name="TTL for expiry",
            expireAfterSeconds=0)

    def activate(
            self, user_oid: ObjectId, source_channel_oid: ObjectId, target_channel_oid: ObjectId,
            locale_code: Optional[str] = None) \
            -> RemoteControlEntryModel:
        """
        Activate the remote control and return the created entry in the holder.

        :return: Created data entry. `None` otherwise if failed to activate.
        """
        model = RemoteControlEntryModel(
            UserOid=user_oid, SourceChannelOid=source_channel_oid, TargetChannelOid=target_channel_oid,
            ExpiryUtc=datetime.utcnow() + timedelta(seconds=Bot.RemoteControl.IdleDeactivateSeconds),
            LocaleCode=locale_code)

        outcome, exception = self.insert_one_model(model)

        return model if outcome.is_success else None

    def deactivate(self, user_oid: ObjectId, source_channel_oid: ObjectId) -> bool:
        """
        Deactivate the remote control for a specific user.

        :return: If the deletion is performed and succeeded
        """
        return self.delete_one({RemoteControlEntryModel.UserOid.key: user_oid,
                                RemoteControlEntryModel.SourceChannelOid.key: source_channel_oid
                                }).deleted_count > 0

    def get_current(self, user_oid: ObjectId, source_channel_oid: ObjectId,
                    *, update_expiry: bool = True) -> Optional[RemoteControlEntryModel]:
        """
        Get the current activating remote control.
        Upon found, update the expiry time if `update_expiry` is set to `True`.

        :return: Current activating remote control. `None` if not found.
        """
        filter_ = {
            RemoteControlEntryModel.UserOid.key: user_oid,
            RemoteControlEntryModel.SourceChannelOid.key: source_channel_oid
        }
        now = now_utc_aware()

        ret = self.find_one_casted(filter_, parse_cls=RemoteControlEntryModel)

        # Entry not found
        if not ret:
            return None

        if update_expiry:
            # Update the object to be returned and the object in the database
            new_expiry = now + timedelta(seconds=Bot.RemoteControl.IdleDeactivateSeconds)

            ret.expiry_utc = new_expiry
            self.update_one_async(filter_, {"$set": {RemoteControlEntryModel.ExpiryUtc.key: new_expiry}})

        # Ensure TTL - TTL may not work under millisecond scale
        if now < ret.expiry_utc:
            return RemoteControlEntryModel.cast_model(ret)
        else:
            return None


RemoteControlManager = _RemoteControlManager()
