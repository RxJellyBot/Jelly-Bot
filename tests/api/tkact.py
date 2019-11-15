# Request Factory - https://stackoverflow.com/a/25835403
# Testing tools - https://docs.djangoproject.com/en/2.2/topics/testing/tools/

import django
from django.test import Client, TestCase

from flags import TokenAction
from mongodb.factory import MONGO_CLIENT, TokenActionManager

c = Client(enforce_csrf_checks=True)
django.setup()


class TestTokenAction(TestCase):
    TEST_ROOT_UID = None
    TEST_TA_TOKEN = None

    @classmethod
    def setUpTestData(cls) -> None:
        from mongodb.factory import RootUserManager
        from extutils.gidentity import GoogleIdentityUserData

        MONGO_CLIENT.get_database("tk_act").get_collection("main").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("api").delete_many({})
        MONGO_CLIENT.get_database("user").get_collection("root").delete_many({})

        # Register Fake API Data
        reg = RootUserManager.register_google(
            GoogleIdentityUserData("Fake", "Fake", "Fake", "Fake@email.com", skip_check=True))
        if reg.success:
            cls.TEST_ROOT_UID = reg.model.id
        else:
            raise ValueError("Fake data registration failed.")

    def test_enqueue_test_action(self):
        self.__class__.TEST_TA_TOKEN = \
            TokenActionManager.enqueue_action(self.__class__.TEST_ROOT_UID, TokenAction.SYS_TEST).token

    def test_token_action_list(self):
        tas = TokenActionManager.get_queued_actions(self.__class__.TEST_ROOT_UID)

        self.assertFalse(tas.alive)

        found = False
        for ta in tas:
            if ta.token == self.__class__.TEST_TA_TOKEN and ta.action_type == TokenAction.SYS_TEST:
                found = True
                break

        self.assertTrue(found)
