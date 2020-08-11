# Request Factory - https://stackoverflow.com/a/25835403
# Testing tools - https://docs.djangoproject.com/en/2.2/topics/testing/tools/

from django.test import TestCase
from django.urls import reverse

from JellyBot.api.static import result as r, param as p
from mongodb.factory import MONGO_CLIENT, ChannelManager

from ._utils import GetJsonResponseMixin


class TestChannelRegistration(GetJsonResponseMixin, TestCase):
    TEST_API_TOKEN = None
    TEST_ROOT_UID = None
    TEST_EXECODE = None

    @classmethod
    def setUpTestData(cls) -> None:
        from mongodb.factory import RootUserManager
        from extutils.gidentity import GoogleIdentityUserData

        MONGO_CLIENT.get_database("execode").get_collection("main").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("dict").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("user").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("perm").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("api").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("root").delete_many({})

        # Register Fake API Data
        reg = RootUserManager.register_google(
            GoogleIdentityUserData("Fake", "Fake", "Fake", "Fake@email.com", skip_check=True))
        if reg.success:
            cls.TEST_API_TOKEN = reg.idt_reg_result.model.token
        else:
            raise ValueError("Fake data registration failed.")

        ChannelManager.ensure_register(1, "channel1")

    def test_main(self):
        self._issue_channel_register_execode()
        self._complete_registration_no_channel_id()
        self._complete_registration()

    def _issue_channel_register_execode(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.id.channel.register_execode"),
            {p.Execode.API_TOKEN: self.TEST_API_TOKEN},
            "Test - Issue Register Execode")

        self.assertTrue(result[r.SUCCESS])
        self.TEST_EXECODE = result[r.RESULT][r.ExecodeResponse.EXECODE]

    def _complete_registration_no_channel_id(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.execode.complete"),
            {p.Execode.EXECODE: self.TEST_EXECODE},
            "Test - Complete Register Execode (no Channel)")

        self.assertFalse(result[r.SUCCESS])

    def _complete_registration(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.execode.complete"),
            {
                p.Execode.EXECODE: self.TEST_EXECODE,
                p.Execode.CHANNEL_TOKEN: "channel1",
                p.Execode.PLATFORM: 1
            },
            "Test - Complete Register Execode (with Channel)")

        self.assertTrue(result[r.SUCCESS])


class TestChannelDataQuery(GetJsonResponseMixin, TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        MONGO_CLIENT.get_database("channel").get_collection("dict").delete_many({})
        ChannelManager.ensure_register(1, "channel1")

    def test_get_existed_data(self):
        result = self.print_and_get_json(
            "GET",
            reverse("api.id.channel.data"),
            {p.DataQuery.Channel.PLATFORM: 1, p.DataQuery.Channel.CHANNEL_TOKEN: "channel1"},
            "Test - Query existed channel data"
        )

        self.assertTrue(result[r.SUCCESS])

    def test_get_non_existed_data(self):
        result = self.print_and_get_json(
            "GET",
            reverse("api.id.channel.data"),
            {p.DataQuery.Channel.PLATFORM: 1, p.DataQuery.Channel.CHANNEL_TOKEN: "channel5"},
            "Test - Query non-existed channel data"
        )

        self.assertFalse(result[r.SUCCESS])
        self.assertTrue(r.RESULT in result)

    def test_get_channel_data_empty_channel_token(self):
        result = self.print_and_get_json(
            "GET",
            reverse("api.id.channel.data"),
            {p.DataQuery.Channel.PLATFORM: 1, p.DataQuery.Channel.CHANNEL_TOKEN: ""},
            "Test - Query channel data with empty channel token"
        )

        self.assertFalse(result[r.SUCCESS])
        self.assertTrue(r.RESULT in result)
        self.assertTrue(result[r.RESULT] is None)
