from django.conf import settings

from extutils.emailutils import EmailServer
from flags import ChannelType, ImageContentType, MessageType, BotFeature
from models import MessageRecordModel, BotFeatureUsageModel
from mongodb.factory import MessageRecordStatisticsManager, BotFeatureUsageDataManager
from msghandle.handle import (
    handle_message_main, load_handling_functions, unload_handling_functions, HandlingFunctionsNotLoadedError
)
from msghandle.models import ImageContent, LineStickerContent, HandledMessageEventsHolder, HandledMessageEventText
from strres.msghandle import HandledResult
from tests.base import TestCase, TestModelMixin, EventFactory

__all__ = ["TestHandleMessageMainEntryPoint", "TestHandleMessageNotLoaded"]


class TestHandleMessageNotLoaded(TestCase):
    @classmethod
    def obj_to_clear(cls):
        return [EventFactory]

    @classmethod
    def setUpTestClass(cls):
        EventFactory.prepare_data()

    def test_not_loaded(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
        with self.assertRaises(HandlingFunctionsNotLoadedError):
            handle_message_main(event)


class TestHandleMessageMainEntryPoint(TestModelMixin):
    @classmethod
    def obj_to_clear(cls):
        return [EventFactory, MessageRecordStatisticsManager, BotFeatureUsageDataManager]

    @classmethod
    def setUpTestClass(cls):
        EventFactory.prepare_data()
        load_handling_functions()

    @classmethod
    def tearDownTestClass(cls):
        unload_handling_functions()

    def test_handle_line_prv_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_gprv_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_gpub_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_prv_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_gprv_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_gpub_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_prv_sticker(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_gprv_sticker(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_gpub_sticker(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_prv_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_LINE_PRV_1_OID,
                                                EventFactory.USER_1_OID, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_gprv_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_LINE_GPRV_1_OID,
                                                EventFactory.USER_1_OID, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_gpub_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_LINE_GPUB_1_OID,
                                                EventFactory.USER_1_OID, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_prv_no_user_token(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_gprv_no_user_token(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_gpub_no_user_token(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_prv_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_line_gprv_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_line_gpub_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_LINE_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_line_prv_text_no_col(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_gprv_text_no_col(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PRV_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_gpub_text_no_col(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PUB_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_line_prv_image_no_col(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_gprv_image_no_col(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PRV_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_gpub_image_no_col(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PUB_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_line_prv_sticker_no_col(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_gprv_sticker_no_col(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.GROUP_PRV_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_gpub_sticker_no_col(self):
        event = EventFactory.generate_line_sticker(LineStickerContent(11952172, 317509841),
                                                   EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                                   ChannelType.GROUP_PUB_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER,
                MessageRecordModel.MessageContent.key: "Package#11952172 / Sticker#317509841"
            }),
            1
        )

    def test_handle_line_prv_unhandled_no_col(self):
        event = EventFactory.generate_unhandled(ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_LINE_PRV_1_OID,
                                                EventFactory.USER_1_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_gprv_unhandled_no_col(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_LINE_GPRV_1_OID,
                                                EventFactory.USER_1_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_gpub_unhandled_no_col(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_LINE_GPUB_1_OID,
                                                EventFactory.USER_1_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_line_prv_no_user_token_no_col(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_PRV_1_OID, None,
                    ChannelType.PRIVATE_TEXT)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            len(MessageRecordStatisticsManager.get_recent_messages(EventFactory.CHANNEL_LINE_PRV_1_OID)),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_gprv_no_user_token_no_col(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_GPRV_1_OID, None,
                    ChannelType.GROUP_PRV_TEXT)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            len(MessageRecordStatisticsManager.get_recent_messages(EventFactory.CHANNEL_LINE_GPRV_1_OID)),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_gpub_no_user_token_no_col(self):
        data = [
            (
                "Text", EventFactory.generate_text(
                    "TEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT)
            ),
            (
                "Image", EventFactory.generate_image(
                    ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                    EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT)
            ),
            (
                "LINE Sticker", EventFactory.generate_line_sticker(
                    LineStickerContent(11952172, 317509841),
                    EventFactory.CHANNEL_LINE_GPUB_1_OID, None,
                    ChannelType.GROUP_PUB_TEXT)
            )
        ]

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        for category, event in data:
            with self.subTest(category):
                self.assertEqual(
                    handle_message_main(event),
                    HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                               [HandledMessageEventText(content=HandledResult.TestFailedNoToken)])
                )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None
            }),
            3
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.TEXT
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.IMAGE
            }),
            1
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: None,
                MessageRecordModel.MessageType.key: MessageType.LINE_STICKER
            }),
            1
        )

    def test_handle_line_prv_error_no_col(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_PRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_line_gprv_error_no_col(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_GPRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PRV_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_line_gpub_error_no_col(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_LINE_GPUB_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PUB_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_LINE_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_LINE_GPUB_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_discord_prv_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_DISCORD_PRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_discord_gprv_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_DISCORD_GPRV_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_discord_gpub_text(self):
        event = EventFactory.generate_text("TEST", EventFactory.CHANNEL_DISCORD_GPUB_1_OID, EventFactory.USER_1_OID,
                                           ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "TEST"
            }),
            1
        )

    def test_handle_discord_prv_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_DISCORD_PRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_discord_gprv_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_DISCORD_GPRV_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_discord_gpub_image(self):
        event = EventFactory.generate_image(ImageContent("https://i.imgur.com/KbnhjEk.png", ImageContentType.URL),
                                            EventFactory.CHANNEL_DISCORD_GPUB_1_OID, EventFactory.USER_1_OID,
                                            ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.TestSuccessImage)])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.IMAGE,
                MessageRecordModel.MessageContent.key: "Image at https://i.imgur.com/KbnhjEk.png, Comment=None"
            }),
            1
        )

    def test_handle_discord_prv_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.PRIVATE_TEXT, EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                                                EventFactory.USER_1_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_PRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_discord_gprv_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PRV_TEXT, EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                                                EventFactory.USER_1_OID, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPRV_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_discord_gpub_unhandled(self):
        event = EventFactory.generate_unhandled(ChannelType.GROUP_PUB_TEXT, EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                                                EventFactory.USER_1_OID, EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPUB_1_OID])
        )
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.UNKNOWN,
                MessageRecordModel.MessageContent.key: None
            }),
            1
        )

    def test_handle_discord_prv_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                                           EventFactory.USER_1_OID, ChannelType.PRIVATE_TEXT)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_PRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_PRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_discord_gprv_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                                           EventFactory.USER_1_OID, ChannelType.GROUP_PRV_TEXT,
                                           EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPRV_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPRV_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )

    def test_handle_discord_gpub_error(self):
        event = EventFactory.generate_text("ERRORTEST", EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                                           EventFactory.USER_1_OID, ChannelType.GROUP_PUB_TEXT,
                                           EventFactory.CHANNEL_COL_DISCORD_OID)

        self.assertEqual(MessageRecordStatisticsManager.count_documents({}), 0)
        self.assertEqual(BotFeatureUsageDataManager.count_documents({}), 0)
        self.assertEqual(
            handle_message_main(event),
            HandledMessageEventsHolder(EventFactory.CHANNEL_MODELS[EventFactory.CHANNEL_DISCORD_GPUB_1_OID],
                                       [HandledMessageEventText(content=HandledResult.ErrorHandle)])
        )
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)
        self.assertEqual(
            MessageRecordStatisticsManager.count_documents({
                MessageRecordModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                MessageRecordModel.UserRootOid.key: EventFactory.USER_1_OID,
                MessageRecordModel.MessageType.key: MessageType.TEXT,
                MessageRecordModel.MessageContent.key: "ERRORTEST"
            }),
            1
        )
        self.assertEqual(
            BotFeatureUsageDataManager.count_documents({
                BotFeatureUsageModel.ChannelOid.key: EventFactory.CHANNEL_DISCORD_GPUB_1_OID,
                BotFeatureUsageModel.SenderRootOid.key: EventFactory.USER_1_OID,
                BotFeatureUsageModel.Feature.key: BotFeature.TXT_FN_ERROR_TEST
            }),
            1
        )
