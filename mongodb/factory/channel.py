from typing import Optional

from flags import Platform
from models import ChannelModel
from mongodb.factory.results import InsertOutcome, ChannelRegistrationResult

from ._base import BaseCollection

DB_NAME = "channel"


class ChannelManager(BaseCollection):
    def __init__(self):
        super().__init__(DB_NAME, "dict", ChannelModel.Token)
        self.create_index([(ChannelModel.Platform, 1), (ChannelModel.Token, 1)],
                          name="Channel Identity", unique=True)

    def register(self, platform: Platform, token: str) -> ChannelRegistrationResult:
        entry, outcome, ex, insert_result = self.insert_one_data(ChannelModel, platform=platform, token=token)

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(ChannelModel.Token, (platform, token), entry)
        elif InsertOutcome.data_found(outcome):
            entry = self.get(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    def get_channel(self, platform: Platform, token: str) -> Optional[ChannelModel]:
        return self.get_cache(ChannelModel.Token, (platform, token), parse_cls=ChannelModel,
                              acquire_args=({ChannelModel.Token: token, ChannelModel.Platform: platform},))


_inst = ChannelManager()
