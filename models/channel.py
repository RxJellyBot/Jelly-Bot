from bson import ObjectId
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from JellyBot.systemconfig import ChannelConfig
from models.field import (
    PlatformField, TextField, ModelField, IntegerField, BooleanField, ObjectIDField, DictionaryField, ArrayField
)

from ._base import Model
from .field import ModelDefaultValueExt


class ChannelConfigModel(Model):
    WITH_OID = False

    # Votes needed to promote a member to be moderator
    VotePromoMod = IntegerField("v-m", default=ChannelConfig.VotesToPromoteMod, positive_only=True)
    # Votes needed to promote a member to be admin
    VotePromoAdmin = IntegerField("v-a", default=ChannelConfig.VotesToPromoteAdmin, positive_only=True)

    EnableAutoReply = BooleanField("e-ar", default=True)
    EnableTimer = BooleanField("e-tmr", default=True)
    EnableCalculator = BooleanField("e-calc", default=True)
    EnableBotCommand = BooleanField("e-bot", default=True)

    InfoPrivate = BooleanField("prv", default=False)

    DefaultProfileOid = ObjectIDField("d-prof", default=ModelDefaultValueExt.Required,
                                      allow_none=False, readonly=False)
    DefaultName = TextField("d-name", allow_none=True)


class ChannelNameField(DictionaryField):
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId, session: ClientSession) -> bool:
        return collection_inst.update_many({}, {"$rename": {f"n.{old}": f"n.{new}"}}, session=session).acknowledged


class ChannelModel(Model):
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)
    Token = TextField("t", default=ModelDefaultValueExt.Required, must_have_content=True)
    Name = ChannelNameField("n", allow_none=False, default={}, stores_uid=True)
    Config = ModelField("c", ChannelConfigModel)
    BotAccessible = BooleanField("acc", default=True)

    def get_channel_name(self, root_oid: ObjectId):
        oid_str = str(root_oid)

        if oid_str in self.name:
            return self.name[oid_str]
        else:
            return self.config.default_name or self.token


class ChannelCollectionModel(Model):
    DefaultName = TextField("dn", default=ModelDefaultValueExt.Required, must_have_content=True)
    Name = DictionaryField("n", allow_none=False, default={})
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)
    Token = TextField("t", default=ModelDefaultValueExt.Required, must_have_content=True)
    BotAccessible = BooleanField("acc", default=True)
    ChildChannelOids = ArrayField("ch", ObjectId)
