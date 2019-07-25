# Request Factory - https://stackoverflow.com/a/25835403
# Testing tools - https://docs.djangoproject.com/en/2.2/topics/testing/tools/
import json
import unittest
import pprint

from django.test import TestCase
from django.urls import reverse

from JellyBotAPI.api.static import result as r, param as p
from models import AutoReplyModuleModel
from mongodb.factory import MONGO_CLIENT
from mongodb.factory.results import InsertOutcome, GetOutcome

from ._utils import GetJsonResponseMixin


class TestAddAutoReply(GetJsonResponseMixin, TestCase):
    TOKEN = None
    FAKE_API_TOKEN = None

    @classmethod
    def setUpTestData(cls) -> None:
        from mongodb.factory import RootUserManager
        from extutils.gidentity import GoogleIdentityUserData

        MONGO_CLIENT.get_database("stats").get_collection("api").delete_many({})
        MONGO_CLIENT.get_database("tk_act").get_collection("main").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("onplat").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("root").delete_many({})
        MONGO_CLIENT.get_database("channel").get_collection("dict").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("conn").delete_many({})
        MONGO_CLIENT.get_database("ar").get_collection("ctnt").delete_many({})

        # Register Fake API Data
        reg = RootUserManager.register_google(
            GoogleIdentityUserData("Fake", "Fake", "Fake", "Fake@email.com", skip_check=True))
        if reg.success:
            cls.FAKE_API_TOKEN = reg.idt_reg_result.model.token
        else:
            raise ValueError("Fake data registration failed.")

    def test_add_using_onplat(self):
        def _add_token_(kw, rep, channel, creator, platform, additional_msg=None):
            ret = self.print_and_get_json(
                "POST",
                reverse("api.ar.add"),
                {
                    p.AutoReply.KEYWORD: kw,
                    p.AutoReply.RESPONSE: rep,
                    p.AutoReply.CHANNEL_TOKEN: channel,
                    p.AutoReply.CREATOR_TOKEN: creator,
                    p.AutoReply.PLATFORM: platform
                },
                f"Test - Add - TOKEN ({None or additional_msg})")

            self.assertTrue(ret[r.SUCCESS])
            return ret

        result = _add_token_("ABC", "mno", "channel1", "user1", 1, "All New")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)

        result = _add_token_("ABC", "mno", "channel1", "user2", 1, "Diff CR")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = _add_token_("ABC", "mno", "channel2", "user2", 1, "Duplicate Conn. New CH.")
        self.assertEqual(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_DATA_EXISTS)

        result = _add_token_("abc2", "mno2", "channel2", "user1", 1, "New Conn. Same User.")
        self.assertEquals(result[r.RESULT][r.Results.OUTCOME], InsertOutcome.O_INSERTED)

    def test_add_using_api(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {
                p.AutoReply.KEYWORD: "AC",
                p.AutoReply.RESPONSE: "BD",
                p.AutoReply.API_TOKEN: self.__class__.FAKE_API_TOKEN,
                p.AutoReply.PLATFORM: 1,
                p.AutoReply.CHANNEL_TOKEN: "channel1",
            },
            f"Test - Add - API")

        self.assertTrue(result[r.SUCCESS])

    def test_lack_of_parameter(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {p.AutoReply.KEYWORD: "xx"},
            f"Test - Add - Lack of Parameter")

        self.assertTrue(r.REQUIRED in result)
        self.assertTrue(p.AutoReply.RESPONSE in result[r.REQUIRED])

    def test_add_empty_content(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {
                p.AutoReply.KEYWORD: "",
                p.AutoReply.RESPONSE: "",
                p.AutoReply.CHANNEL_TOKEN: "channel1",
                p.AutoReply.CREATOR_TOKEN: "user1",
                p.AutoReply.PLATFORM: 1
            },
            f"Test - Add - Empty Content Module")

        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.KEYWORD][r.Results.OUTCOME], GetOutcome.X_NO_CONTENT)
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.RESPONSES][0][r.Results.OUTCOME], GetOutcome.X_NO_CONTENT)
        self.assertFalse(result[r.SUCCESS])

    def test_add_empty_channel_token(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {
                p.AutoReply.KEYWORD: "A",
                p.AutoReply.RESPONSE: "B",
                p.AutoReply.CHANNEL_TOKEN: "",
                p.AutoReply.CREATOR_TOKEN: "user1",
                p.AutoReply.PLATFORM: 1
            },
            f"Test - Add - Empty Channel Token")

        self.assertTrue(r.AutoReplyResponse.CHANNEL_OID in result[r.ERRORS])
        self.assertEqual(result[r.ERRORS][r.AutoReplyResponse.CHANNEL_OID], "")
        self.assertFalse(result[r.SUCCESS])

    def test_add_empty_user_token(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {
                p.AutoReply.KEYWORD: "A",
                p.AutoReply.RESPONSE: "B",
                p.AutoReply.CHANNEL_TOKEN: "channel1",
                p.AutoReply.CREATOR_TOKEN: "",
                p.AutoReply.PLATFORM: 1
            },
            f"Test - Add - Empty Channel Token")

        self.assertTrue(r.SenderIdentity.SENDER in result[r.ERRORS])
        # Creator OID is a Processed value (via `Middleware`)
        self.assertEqual(result[r.ERRORS][r.SenderIdentity.SENDER], None)
        self.assertFalse(result[r.SUCCESS])

    def test_add_token(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add_token"),
            {
                p.AutoReply.KEYWORD: "R",
                p.AutoReply.RESPONSE: "X",
                p.AutoReply.CHANNEL_TOKEN: "channel1",
                p.AutoReply.CREATOR_TOKEN: "user1",
                p.AutoReply.PLATFORM: 1
            },
            f"Test - Add - Token")
        
        self.assertTrue(result[r.SUCCESS])
        self.assertTrue(r.TokenActionResponse.TOKEN in result[r.RESULT])
        self.__class__.TOKEN = result[r.RESULT][r.TokenActionResponse.TOKEN]

    def test_add_token_complete(self):
        token = self.__class__.TOKEN
        if token is None:
            raise ValueError("Token action not performed yet.")

        result = self.print_and_get_json(
            "POST",
            reverse("api.token.complete"),
            {
                p.TokenAction.TOKEN: token,
                p.AutoReply.CHANNEL_TOKEN: "channel1",
                p.AutoReply.PLATFORM: 1
            },
            f"Test - Add - Token Complete")

        self.assertTrue(result[r.SUCCESS])

    def test_add_with_tags(self):
        result = self.print_and_get_json(
            "POST",
            reverse("api.ar.add"),
            {
                p.AutoReply.KEYWORD: "AC",
                p.AutoReply.RESPONSE: "BD",
                p.AutoReply.TAGS: "A|B|C",
                p.AutoReply.API_TOKEN: self.__class__.FAKE_API_TOKEN,
                p.AutoReply.PLATFORM: 1,
                p.AutoReply.CHANNEL_TOKEN: "channel1",
            },
            f"Test - Add - API w/ Tags")

        self.assertTrue(result[r.SUCCESS])
        self.assertTrue(len(result[r.RESULT][r.Results.MODEL][AutoReplyModuleModel.TagIds.key]) > 0)


if __name__ == '__main__':
    unittest.main()
