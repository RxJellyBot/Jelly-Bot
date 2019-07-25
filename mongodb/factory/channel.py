from typing import Optional

from bson import ObjectId

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
        super().__init__(self.CACHE_KEY_SPEC1)
        self.create_index([(ChannelModel.Platform.key, 1), (ChannelModel.Token.key, 1)],
                          name="Channel Identity", unique=True)

    @DecoParamCaster({1: Platform, 2: str})
    def register(self, platform: Platform, token: str) -> ChannelRegistrationResult:
        entry, outcome, ex, insert_result = self.insert_one_data(
            ChannelModel, Platform=platform, Token=token, Config=ChannelConfigModel.generate_default())

        if InsertOutcome.is_inserted(outcome):
            self.set_cache(self.CACHE_KEY_SPEC1, (platform, token), entry)
        elif InsertOutcome.data_found(outcome):
            entry = self.get_channel_token(platform, token)

        return ChannelRegistrationResult(outcome, entry, ex)

    @DecoParamCaster({1: Platform, 2: str})
    def get_channel_token(self, platform: Platform, token: str) -> Optional[ChannelModel]:
        return self.get_cache(self.CACHE_KEY_SPEC1, (platform, token), parse_cls=ChannelModel,
                              acquire_args=({ChannelModel.Token.key: token, ChannelModel.Platform.key: platform},))

    @DecoParamCaster({1: ObjectId})
    def get_channel_oid(self, channel_oid: ObjectId) -> Optional[ChannelModel]:
        return self.get_cache_condition(
            self.CACHE_KEY_SPEC1, lambda item: item.id == channel_oid, parse_cls=ChannelModel,
            acquire_args=({ChannelModel.Id.key: channel_oid},))

    # noinspection PyArgumentList
    @DecoParamCaster({1: Platform, 2: str})
    def get_channel_packed(self, platform: Platform, token: str) -> ChannelGetResult:
        if not isinstance(platform, Platform):
            platform = Platform(platform)

        model = self.get_channel_token(platform, token)

        if model is not None:
            outcome = GetOutcome.O_CACHE_DB
        else:
            outcome = GetOutcome.X_NOT_FOUND_ABORTED_INSERT

        return ChannelGetResult(outcome, model)

    def set_config(self, channel_oid: ObjectId, json_key, config_value) -> bool:
        if json_key not in ChannelConfigModel.model_json():
            raise ValueError(f"Attempt to set value to non-existing field in `ChannelModel`. ({json_key})")

        filter_ = {ChannelModel.Id.key: channel_oid}

        found_any = self.update_one(
            filter_,
            {"$set": {f"{ChannelModel.Config.key}.{json_key}": config_value}}).matched_count > 0

        if found_any:
            model = ChannelConfigModel(**self.find_one(filter_)[ChannelModel.Config.key], from_db=True)

            self.set_cache(self.CACHE_KEY_SPEC1, (model.platform, model.token), model, parse_cls=ChannelModel)

        return found_any


_inst = ChannelManager()
