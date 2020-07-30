import time
from abc import ABC
from threading import Thread
from typing import Any, Optional, Union

from bson import ObjectId
from linebot.models import TextMessage, ImageMessage, StickerMessage, MessageEvent
from discord import Message, ChannelType

from models import ChannelModel, RootUserModel, ChannelCollectionModel
from mongodb.factory import ChannelManager, RootUserManager, ChannelCollectionManager, RemoteControlManager
from extutils.emailutils import MailSender
from msghandle import logger
from msghandle.models import ImageContent, LineStickerContent
from flags import Platform, MessageType, ChannelType as SysChannelType, ImageContentType


class Event(ABC):
    def __init__(
            self, raw: Any, channel_model: ChannelModel = None, sys_ctype: SysChannelType = None,
            source_channel: ChannelModel = None):
        if not sys_ctype:
            sys_ctype = SysChannelType.identify(channel_model.platform, channel_model.token)

        if not source_channel:
            source_channel = channel_model

        self._construct = time.time()

        self.raw = raw
        self.channel_model = channel_model
        self.channel_model_source = source_channel
        self.channel_type = sys_ctype
        self.remote_activated = self.channel_model != self.channel_model_source

    @property
    def platform(self) -> Platform:
        return self.channel_model.platform

    @property
    def platform_src(self) -> Platform:
        return self.channel_model_source.platform

    @property
    def user_token(self) -> Optional[Union[int, str]]:
        if self.platform_src == Platform.LINE:
            from extline import LineApiUtils

            return LineApiUtils.get_user_id(self.raw)
        elif self.platform_src == Platform.DISCORD:
            return self.raw.author.id
        else:
            return None

    @property
    def constructed_time(self) -> float:
        """The unit of this is seconds."""
        return time.time() - self._construct


class MessageEventObject(Event, ABC):
    def __init__(
            self, raw: Any, content: Any, channel_model: ChannelModel = None,
            user_model: Optional[RootUserModel] = None,
            sys_ctype: SysChannelType = None, ch_parent_model: ChannelCollectionModel = None):
        src_ch = None

        rmc = None
        if user_model:
            rmc = RemoteControlManager.get_current(user_model.id, channel_model.id)

        if rmc:
            src_ch = channel_model
            channel_model = rmc.target_channel

        super().__init__(raw, channel_model, sys_ctype, source_channel=src_ch)
        self.content = content
        self.user_model = user_model
        self.chcoll_model = ch_parent_model

    @property
    def message_type(self) -> MessageType:
        raise NotImplementedError()

    @property
    def channel_oid(self) -> ObjectId:
        return self.channel_model.id

    @property
    def root_oid(self) -> Optional[ObjectId]:
        if self.user_model:
            return self.user_model.id
        else:
            return None


class TextMessageEventObject(MessageEventObject):
    def __init__(
            self, raw: Any, text: str, channel_model: ChannelModel = None, user_model: Optional[RootUserModel] = None,
            sys_ctype: SysChannelType = None, ch_parent_model: ChannelCollectionModel = None):
        text = text.strip()

        super().__init__(raw, text, channel_model, user_model, sys_ctype, ch_parent_model)

    @property
    def message_type(self) -> MessageType:
        return MessageType.TEXT

    @property
    def text(self) -> str:
        return self.content


class ImageMessageEventObject(MessageEventObject):
    def __init__(
            self, raw: Any, image: ImageContent, channel_model: ChannelModel = None,
            user_model: Optional[RootUserModel] = None, sys_ctype: SysChannelType = None,
            ch_parent_model: ChannelCollectionModel = None):
        super().__init__(raw, image, channel_model, user_model, sys_ctype, ch_parent_model)

    @property
    def message_type(self) -> MessageType:
        return MessageType.IMAGE


class LineStickerMessageEventObject(MessageEventObject):
    def __init__(
            self, raw: Any, sticker: LineStickerContent, channel_model: ChannelModel = None,
            user_model: Optional[RootUserModel] = None, sys_ctype: SysChannelType = None,
            ch_parent_model: ChannelCollectionModel = None):
        super().__init__(raw, sticker, channel_model, user_model, sys_ctype, ch_parent_model)

    @property
    def message_type(self) -> MessageType:
        return MessageType.LINE_STICKER


class MessageEventObjectFactory:
    DiscordAcceptedChannelTypes = (ChannelType.text, ChannelType.private, ChannelType.group)

    @staticmethod
    def _ensure_channel_(platform: Platform, token: Union[int, str], default_name: str = None) \
            -> Optional[ChannelModel]:
        ret = ChannelManager.register(platform, token, default_name=default_name)
        if ret.success:
            # Use Thread so no need to wait until the update is completed
            Thread(target=ChannelManager.mark_accessibility, args=(platform, token, True)).start()
        else:
            MailSender.send_email_async(f"Platform: {platform} / Token: {token}",
                                        subject="Channel Registration Failed")

        return ret.model

    @staticmethod
    def _ensure_user_idt_(platform: Platform, token: Union[int, str]) -> Optional[RootUserModel]:
        if token:
            result = RootUserManager.register_onplat(platform, token)
            if not result.success:
                MailSender.send_email_async(
                    f"Platform: {platform} / Token: {token}<hr>"
                    f"Outcome: {result.outcome}<hr>"
                    f"Conn Outcome: {result.conn_outcome}<hr>"
                    f"Identity Registration Result: {result.idt_reg_result.serialize()}",
                    subject="User Registration Failed")

            return result.model
        else:
            return None

    @staticmethod
    def _ensure_channel_parent_(
            platform: Platform, token: Union[int, str], child_channel_oid: ObjectId, default_name: str):
        return ChannelCollectionManager.register(platform, token, child_channel_oid, default_name).model

    @staticmethod
    def from_line(event: MessageEvent, destination: str) -> MessageEventObject:
        from extline import LineApiUtils, LineApiWrapper

        user_model = MessageEventObjectFactory._ensure_user_idt_(
            Platform.LINE, LineApiUtils.get_user_id(event, destination))
        channel_model = MessageEventObjectFactory._ensure_channel_(
            Platform.LINE, LineApiUtils.get_channel_id(event), LineApiUtils.get_channel_id(event))

        if isinstance(event.message, TextMessage):
            return TextMessageEventObject(
                event, event.message.text, channel_model, user_model)
        elif isinstance(event.message, ImageMessage):
            return ImageMessageEventObject(
                event, ImageContent(LineApiWrapper.get_image_base64(event.message), ImageContentType.BASE64),
                channel_model, user_model)
        elif isinstance(event.message, StickerMessage):
            return LineStickerMessageEventObject(
                event, LineStickerContent(package_id=event.message.package_id, sticker_id=event.message.sticker_id),
                channel_model, user_model)
        else:
            logger.logger.warning(f"Unhandled LINE message event. {type(event.message)}")

    @staticmethod
    def from_discord(message: Message) -> Optional[MessageEventObject]:
        from extdiscord.utils import msg_loc_repr

        if message.channel.type not in MessageEventObjectFactory.DiscordAcceptedChannelTypes:
            raise ValueError(
                f"Channel type not supported. ({message.channel.type})"
                f"Currently supported channel types: "
                f"{', '.join([str(t) for t in MessageEventObjectFactory.DiscordAcceptedChannelTypes])}")

        user_model = MessageEventObjectFactory._ensure_user_idt_(
            Platform.DISCORD, message.author.id)
        channel_model = MessageEventObjectFactory._ensure_channel_(
            Platform.DISCORD, message.channel.id, msg_loc_repr(message))
        if message.guild:
            ch_parent_model = MessageEventObjectFactory._ensure_channel_parent_(
                Platform.DISCORD, message.guild.id, channel_model.id, str(message.guild))
        else:
            ch_parent_model = None

        # If the message contains attachments, then consider it as an Image Message.
        if message.attachments:
            attachment = message.attachments[0]

            # Attachment has height and width means it's an image
            if attachment.height and attachment.width:
                return ImageMessageEventObject(
                    message, ImageContent(attachment.url, ImageContentType.URL, message.content),
                    channel_model, user_model, SysChannelType.trans_from_discord(message.channel.type), ch_parent_model
                )
            else:
                # Discord message has attachment, no corresponding message event object / not implemented
                return None
        else:
            return TextMessageEventObject(
                message, message.content, channel_model, user_model,
                SysChannelType.trans_from_discord(message.channel.type), ch_parent_model
            )
