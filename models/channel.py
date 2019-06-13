from JellyBotAPI.SystemConfig import ChannelConfig
from models import Model
from models.field import PlatformField, TextField, DictionaryField, IntegerField, BooleanField


class ChannelModel(Model):
    Platform = "p"
    Token = "t"
    Config = "c"

    def _init_fields_(self, **kwargs):
        self.platform = PlatformField(ChannelModel.Platform)
        self.token = TextField(ChannelModel.Token, must_have_content=True)
        self.config = DictionaryField(ChannelModel.Config)


class ChannelConfigModel(Model):
    # INCOMPLETE: Channel Config: Default value handling / auto missing field repairing
    # INCOMPLETE: Channel Config: Turn on/off functions (Enable*) by votes if no mod/admin (% of 5 days active member)

    VoteToPromoteMod = "vm"
    VoteToPromoteAdmin = "va"
    EnableAutoReply = "ar"

    def _init_fields_(self, **kwargs):
        self.vote_promo_mod = IntegerField(ChannelConfigModel.VoteToPromoteMod, ChannelConfig.VotesToPromoteMod)
        self.vote_promo_admin = IntegerField(ChannelConfigModel.VoteToPromoteAdmin, ChannelConfig.VotesToPromoteAdmin)
        self.enable_auto_reply = BooleanField(ChannelConfigModel.EnableAutoReply)
