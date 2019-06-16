from JellyBotAPI.SystemConfig import ChannelConfig
from models.field import PlatformField, TextField, ModelField, IntegerField, BooleanField


from ._mixin import CreateDefaultMixin
from ._base import Model, ModelDefaultValueExtension


class ChannelConfigModel(CreateDefaultMixin, Model):
    # INCOMPLETE: Channel Config - Turn on/off functions (Enable*) by votes if no mod/admin (% of 5 days active member)

    VoteToPromoteMod = "vm"
    VoteToPromoteAdmin = "va"
    EnableAutoReply = "ar"
    EnableCreateRole = "cro"

    default_vals = (
        (VoteToPromoteMod, True),
        (VoteToPromoteAdmin, True),
        (EnableAutoReply, True),
        (EnableCreateRole, True)
    )

    def _init_fields_(self, **kwargs):
        self.vote_promo_mod = IntegerField(ChannelConfigModel.VoteToPromoteMod, ChannelConfig.VotesToPromoteMod)
        self.vote_promo_admin = IntegerField(ChannelConfigModel.VoteToPromoteAdmin, ChannelConfig.VotesToPromoteAdmin)
        self.enable_auto_reply = BooleanField(ChannelConfigModel.EnableAutoReply)
        self.enable_create_role = BooleanField(ChannelConfigModel.EnableCreateRole)


class ChannelModel(Model):
    Platform = "p"
    Token = "t"
    Config = "c"

    default_vals = (
        (Platform, ModelDefaultValueExtension.Required),
        (Token, ModelDefaultValueExtension.Required),
        (Config, ChannelConfigModel.create_default().serialize())
    )

    dict_models = (
        (Config, ChannelConfigModel),
    )

    def _init_fields_(self, **kwargs):
        self.platform = PlatformField(ChannelModel.Platform)
        self.token = TextField(ChannelModel.Token, must_have_content=True)
        self.config = ModelField(ChannelModel.Config, ChannelConfigModel)
