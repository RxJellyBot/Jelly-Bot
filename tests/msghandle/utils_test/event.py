from typing import Optional

from bson import ObjectId

from flags import ChannelType, Platform, MessageType
from mixin import ClearableMixin
from models import ChannelModel, ChannelConfigModel, ChannelCollectionModel, RootUserModel, OnPlatformUserModel
from mongodb.factory.channel import ChannelManager, ChannelCollectionManager
from mongodb.factory.user import OnPlatformIdentityManager, RootUserManager
from msghandle.models import (
    TextMessageEventObject, ImageMessageEventObject, LineStickerMessageEventObject, ImageContent, LineStickerContent,
    MessageEventObject
)

__all__ = ["EventFactory"]


class TestUnhandledEventObject(MessageEventObject):
    @property
    def message_type(self) -> MessageType:
        return MessageType.UNKNOWN


class EventFactory(ClearableMixin):
    CHANNEL_LINE_PRV_1_OID = ObjectId()
    CHANNEL_LINE_PRV_2_OID = ObjectId()
    CHANNEL_LINE_GPRV_1_OID = ObjectId()
    CHANNEL_LINE_GPRV_2_OID = ObjectId()
    CHANNEL_LINE_GPUB_1_OID = ObjectId()
    CHANNEL_LINE_GPUB_2_OID = ObjectId()
    CHANNEL_DISCORD_PRV_1_OID = ObjectId()
    CHANNEL_DISCORD_PRV_2_OID = ObjectId()
    CHANNEL_DISCORD_GPRV_1_OID = ObjectId()
    CHANNEL_DISCORD_GPRV_2_OID = ObjectId()
    CHANNEL_DISCORD_GPUB_1_OID = ObjectId()
    CHANNEL_DISCORD_GPUB_2_OID = ObjectId()

    PROF_LINE_PRV_1_OID = ObjectId()
    PROF_LINE_PRV_2_OID = ObjectId()
    PROF_LINE_GPRV_1_OID = ObjectId()
    PROF_LINE_GPRV_2_OID = ObjectId()
    PROF_LINE_GPUB_1_OID = ObjectId()
    PROF_LINE_GPUB_2_OID = ObjectId()
    PROF_DISCORD_PRV_1_OID = ObjectId()
    PROF_DISCORD_PRV_2_OID = ObjectId()
    PROF_DISCORD_GPRV_1_OID = ObjectId()
    PROF_DISCORD_GPRV_2_OID = ObjectId()
    PROF_DISCORD_GPUB_1_OID = ObjectId()
    PROF_DISCORD_GPUB_2_OID = ObjectId()

    CHANNEL_MODELS = {
        CHANNEL_LINE_PRV_1_OID:
            ChannelModel(Id=CHANNEL_LINE_PRV_1_OID, Platform=Platform.LINE, Token="LINE_Private_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_PRV_1_OID)),
        CHANNEL_LINE_PRV_2_OID:
            ChannelModel(Id=CHANNEL_LINE_PRV_2_OID, Platform=Platform.LINE, Token="LINE_Private_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_PRV_2_OID)),
        CHANNEL_LINE_GPRV_1_OID:
            ChannelModel(Id=CHANNEL_LINE_GPRV_1_OID, Platform=Platform.LINE, Token="LINE_GroupPrivate_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_GPRV_1_OID)),
        CHANNEL_LINE_GPRV_2_OID:
            ChannelModel(Id=CHANNEL_LINE_GPRV_2_OID, Platform=Platform.LINE, Token="LINE_GroupPrivate_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_GPRV_2_OID)),
        CHANNEL_LINE_GPUB_1_OID:
            ChannelModel(Id=CHANNEL_LINE_GPUB_1_OID, Platform=Platform.LINE, Token="LINE_GroupPublic_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_GPUB_1_OID)),
        CHANNEL_LINE_GPUB_2_OID:
            ChannelModel(Id=CHANNEL_LINE_GPUB_2_OID, Platform=Platform.LINE, Token="LINE_GroupPublic_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_LINE_GPUB_2_OID)),
        CHANNEL_DISCORD_PRV_1_OID:
            ChannelModel(Id=CHANNEL_DISCORD_PRV_1_OID, Platform=Platform.LINE, Token="Discord_Private_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_PRV_1_OID)),
        CHANNEL_DISCORD_PRV_2_OID:
            ChannelModel(Id=CHANNEL_DISCORD_PRV_2_OID, Platform=Platform.LINE, Token="Discord_Private_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_PRV_2_OID)),
        CHANNEL_DISCORD_GPRV_1_OID:
            ChannelModel(Id=CHANNEL_DISCORD_GPRV_1_OID, Platform=Platform.LINE, Token="Discord_GroupPrivate_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_GPRV_1_OID)),
        CHANNEL_DISCORD_GPRV_2_OID:
            ChannelModel(Id=CHANNEL_DISCORD_GPRV_2_OID, Platform=Platform.LINE, Token="Discord_GroupPrivate_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_GPRV_2_OID)),
        CHANNEL_DISCORD_GPUB_1_OID:
            ChannelModel(Id=CHANNEL_DISCORD_GPUB_1_OID, Platform=Platform.LINE, Token="Discord_GroupPublic_1",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_GPUB_1_OID)),
        CHANNEL_DISCORD_GPUB_2_OID:
            ChannelModel(Id=CHANNEL_DISCORD_GPUB_2_OID, Platform=Platform.LINE, Token="Discord_GroupPublic_2",
                         Config=ChannelConfigModel(DefaultProfileOid=PROF_DISCORD_GPUB_2_OID))
    }

    CHANNEL_COL_LINE_OID = ObjectId()
    CHANNEL_COL_DISCORD_OID = ObjectId()

    CHANNEL_COL_MODELS = {
        CHANNEL_COL_LINE_OID:
            ChannelCollectionModel(Id=CHANNEL_COL_LINE_OID,
                                   DefaultName="Test LINE default group collection",
                                   Platform=Platform.LINE, Token="LINE Group Collection"),
        CHANNEL_COL_DISCORD_OID:
            ChannelCollectionModel(Id=CHANNEL_COL_DISCORD_OID,
                                   DefaultName="Test Discord default group collection",
                                   Platform=Platform.LINE, Token="Discord Group Collection")
    }

    ONPLAT_LINE_1_OID = ObjectId()
    ONPLAT_LINE_2_OID = ObjectId()
    ONPLAT_DISCORD_1_OID = ObjectId()
    ONPLAT_DISCORD_2_OID = ObjectId()

    ON_PLAT_MODELS = {
        ONPLAT_LINE_1_OID: OnPlatformUserModel(Id=ONPLAT_LINE_1_OID, Platform=Platform.LINE,
                                               Token="LINE_User_1"),
        ONPLAT_LINE_2_OID: OnPlatformUserModel(Id=ONPLAT_LINE_2_OID, Platform=Platform.LINE,
                                               Token="LINE_User_2"),
        ONPLAT_DISCORD_1_OID: OnPlatformUserModel(Id=ONPLAT_DISCORD_1_OID, Platform=Platform.DISCORD,
                                                  Token="Discord_User_1"),
        ONPLAT_DISCORD_2_OID: OnPlatformUserModel(Id=ONPLAT_DISCORD_2_OID, Platform=Platform.DISCORD,
                                                  Token="Discord_User_2")
    }

    USER_1_OID = ObjectId()
    USER_2_OID = ObjectId()

    USER_MODELS = {
        USER_1_OID: RootUserModel(Id=USER_1_OID, OnPlatOids=[ONPLAT_LINE_1_OID, ONPLAT_DISCORD_1_OID]),
        USER_2_OID: RootUserModel(Id=USER_1_OID, OnPlatOids=[ONPLAT_LINE_2_OID, ONPLAT_DISCORD_2_OID]),
        None: None  # No user token
    }

    @classmethod
    def clear(cls):
        ChannelManager.clear()
        ChannelCollectionManager.clear()
        OnPlatformIdentityManager.clear()
        RootUserManager.clear()

    @classmethod
    def prepare_data(cls):
        ChannelManager.insert_many(cls.CHANNEL_MODELS.values())
        ChannelCollectionManager.insert_many(cls.CHANNEL_COL_MODELS.values())
        OnPlatformIdentityManager.insert_many(cls.ON_PLAT_MODELS.values())
        RootUserManager.insert_many(cls.ON_PLAT_MODELS.values())

    @classmethod
    def generate_text(cls, text: str,
                      channel_oid: ObjectId, user_oid: Optional[ObjectId],
                      channel_type: ChannelType, channel_collection_oid: Optional[ObjectId] = None):
        return TextMessageEventObject(None, text,
                                      cls.CHANNEL_MODELS[channel_oid], cls.USER_MODELS[user_oid],
                                      channel_type, cls.CHANNEL_COL_MODELS.get(channel_collection_oid),
                                      is_test_event=True)

    @classmethod
    def generate_image(cls, img_content: ImageContent,
                       channel_oid: ObjectId, user_oid: Optional[ObjectId],
                       channel_type: ChannelType, channel_collection_oid: Optional[ObjectId] = None):
        return ImageMessageEventObject(None, img_content,
                                       cls.CHANNEL_MODELS[channel_oid], cls.USER_MODELS[user_oid],
                                       channel_type, cls.CHANNEL_COL_MODELS.get(channel_collection_oid),
                                       is_test_event=True)

    @classmethod
    def generate_line_sticker(cls, sticker_content: LineStickerContent,
                              channel_oid: ObjectId, user_oid: Optional[ObjectId],
                              channel_type: ChannelType, channel_collection_oid: Optional[ObjectId] = None):
        return LineStickerMessageEventObject(None, sticker_content,
                                             cls.CHANNEL_MODELS[channel_oid], cls.USER_MODELS[user_oid],
                                             channel_type, cls.CHANNEL_COL_MODELS.get(channel_collection_oid),
                                             is_test_event=True)

    @classmethod
    def generate_unhandled(cls, channel_type: ChannelType, channel_oid: Optional[ObjectId] = None,
                           user_oid: Optional[ObjectId] = None, channel_collection_oid: Optional[ObjectId] = None):
        return TestUnhandledEventObject(None, None,
                                        sys_ctype=channel_type, channel_model=cls.CHANNEL_MODELS.get(channel_oid),
                                        user_model=cls.USER_MODELS.get(user_oid),
                                        ch_parent_model=cls.CHANNEL_COL_MODELS.get(channel_collection_oid),
                                        is_test_event=True)
