from typing import Optional

from extutils.checker import DecoParamCaster
from flags import Platform
from models import ChannelModel, ChannelConfigModel
from mongodb.factory.results import InsertOutcome, GetOutcome, ChannelRegistrationResult, ChannelGetResult
from ._base import BaseCollection

DB_NAME = "channel"


class ChannelManager(BaseCollection):
    database_name = DB_NAME
    collection_name = "dict"
    model_class = ChannelModel

    def __init__(self):
        super().__init__(ChannelModel.Token.key)
        self.create_index([(ChannelModel.Platform.key, 1), (ChannelModel.Token.key, 1)],
                          name="Channel Identity", unique=True)

    @DecoParamCaster({1: Platform, 2: str})
    def register(self, platform: Platform, token: str) -> ChannelRegistrationResult:
        entry, outcome, ex, insert_result = self.insert_one_data(
            ChannelModel, Platform=platform, Token=token, Config=ChannelConfigModel.generate_default())

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(ChannelModel.Token.key, (platform, token), entry)
        elif InsertOutcome.data_found(outcome):
            entry = self.get_channel(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    @DecoParamCaster({1: Platform, 2: str})
    def get_channel(self, platform: Platform, token: str) -> Optional[ChannelModel]:
        return self.get_cache(ChannelModel.Token.key, (platform, token), parse_cls=ChannelModel,
                              acquire_args=({ChannelModel.Token.key: token, ChannelModel.Platform.key: platform},))

    @DecoParamCaster({1: Platform, 2: str})
    def get_channel_packed(self, platform: Platform, token: str) -> ChannelGetResult:
        """
        Insertion attempt not implemented.
        """
        if not isinstance(platform, Platform):
            platform = Platform(platform)

        model = self.get_channel(platform, token)

        if model is not None:
            outcome = GetOutcome.SUCCESS_CACHE_DB
        else:
            outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT

        return ChannelGetResult(outcome, model)


_inst = ChannelManager()
