# Request Factory - https://stackoverflow.com/a/25835403
# Testing tools - https://docs.djangoproject.com/en/2.2/topics/testing/tools/

import django
from django.test import Client, TestCase

from flags import Execode
from mongodb.factory import MONGO_CLIENT, ExecodeManager

c = Client(enforce_csrf_checks=True)
django.setup()


class TestExecode(TestCase):
    TEST_ROOT_UID = None
    TEST_EXCDE_TOKEN = None

    @classmethod
    def setUpTestData(cls) -> None:
        from mongodb.factory import RootUserManager
        from extutils.gidentity import GoogleIdentityUserData

        MONGO_CLIENT.get_database("execode").get_collection("main").delete_many({})
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
        self.__class__.TEST_EXCDE_TOKEN = \
            ExecodeManager.enqueue_execode(self.__class__.TEST_ROOT_UID, Execode.SYS_TEST).execode

    def test_execode_list(self):
        excdes = ExecodeManager.get_queued_execodes(self.__class__.TEST_ROOT_UID)

        self.assertFalse(excdes.empty)

        found = False
        for excde in excdes:
            if excde.execode == self.__class__.TEST_EXCDE_TOKEN and excde.action_type == Execode.SYS_TEST:
                found = True
                break

        self.assertTrue(found)
