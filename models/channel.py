from JellyBotAPI.SystemConfig import ChannelConfig
from models.field import (
    PlatformField, TextField, ModelField, IntegerField, BooleanField, ObjectIDField
)


from ._base import Model, ModelDefaultValueExt


class ChannelConfigModel(Model):
    # INCOMPLETE: Channel Config - Turn on/off features (Enable*) by votes if no mod/admin (% of 5 days active member)
    # INCOMPLETE: Channel Config - Vote = 0 means no promo

    WITH_OID = False

    VotePromoMod = IntegerField("v-m", default=ChannelConfig.VotesToPromoteMod)
    VotePromoAdmin = IntegerField("v-a", default=ChannelConfig.VotesToPromoteAdmin)
    EnableAutoReply = BooleanField("e-ar", default=True)
    EnableCreateRole = BooleanField("e-cro", default=True)
    DefaultProfileOid = ObjectIDField("d-prof", allow_none=True)


class ChannelModel(Model):
    Platform = PlatformField("p", default=ModelDefaultValueExt.Required)
    Token = TextField("t", default=ModelDefaultValueExt.Required, must_have_content=True)
    Config = ModelField("c", ChannelConfigModel)


class ChannelRegisterExistenceModel(Model):
    RootOid = ObjectIDField("u")
