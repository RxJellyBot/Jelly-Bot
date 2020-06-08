from abc import ABC
from datetime import datetime

from bson import ObjectId

from flags import AutoReplyContentType, PermissionLevel, ProfilePermission, Platform
from models import AutoReplyContentModel, AutoReplyModuleModel
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.factory.ar_conn import AutoReplyModuleManager
from tests.base import TestModelMixin

from ._base_mod_sample import TestArModuleSample

__all__ = ["TestAutoReplyManagerBase"]


class TestAutoReplyManagerBase(ABC):
    class TestClass(TestModelMixin, TestArModuleSample.TestClass):
        CREATOR_OID = ObjectId()
        CREATOR_OID_2 = ObjectId()

        @staticmethod
        def collections_to_reset():
            return [AutoReplyModuleManager]

        def setUpTestCase(self) -> None:
            self.channel_oid = ObjectId()

        def grant_access_pin_permission(self):
            reg_result = ChannelManager.ensure_register(Platform.LINE, "U123456")
            if reg_result.success:
                self.channel_oid = reg_result.model.id
            else:
                self.fail(reg_result.outcome)

            prof = ProfileManager.register_new(
                self.CREATOR_OID, {"ChannelOid": self.channel_oid, "PermissionLevel": PermissionLevel.ADMIN})
            ProfileManager.attach_profile(self.channel_oid, self.CREATOR_OID, prof.get_oid())

            perms = ProfileManager.get_user_permissions(self.channel_oid, self.CREATOR_OID)

            if ProfilePermission.AR_ACCESS_PINNED_MODULE not in perms:
                self.fail("Permission to access pinned module not granted.")

        def _add_call_module_kw_a(self):
            """
            This method perform actions in the following order:

            - Add a module ``Keyword=A, Responses=B``

            - Call the above module 4 times

            - Add a module ``Keyword=A, Responses=C``, overwriting the module mentioned in ``1.``

            - Call the above module 3 times

            - Add a module ``Keyword=A, Responses=D``, overwriting the module mentioned in ``2.``

            - Return the OIDs of these modules in order.

            :return: OIDs of the module added
            """
            # noinspection PyListCreation
            oids = []

            mdl = AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid, CalledCount=4, Active=False
            )
            AutoReplyModuleManager.insert_one_model(mdl)
            oids.append(mdl.id)

            mdl = AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid, CalledCount=3, Active=False
            )
            AutoReplyModuleManager.insert_one_model(mdl)
            oids.append(mdl.id)

            mdl = AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid
            )
            AutoReplyModuleManager.insert_one_model(mdl)
            oids.append(mdl.id)

            return oids

        def _add_call_module_multi(self):
            """
            This method perform actions in the following order:

            -  Actions in ``_add_call_module_kw_a()``

            -  Add a module ``Keyword=B, Responses=C``

            -  Call the above module 9 times

            -  Add a module ``Keyword=C, Responses=C``

            -  Add a module ``Keyword=D, Responses=C``
            """
            self._add_call_module_kw_a()

            AutoReplyModuleManager.insert_one_model(AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid, CalledCount=9
            ))

            AutoReplyModuleManager.insert_one_model(AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid
            ))

            AutoReplyModuleManager.insert_one_model(AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid
            ))

            AutoReplyModuleManager.insert_one_model(AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
                Id=ObjectId.from_datetime(datetime(2020, 5, 7))
            ))

        def _check_model_exists(self, model: AutoReplyModuleModel) -> AutoReplyModuleModel:
            kw = model.keyword.content
            kw_type = model.keyword.content_type

            mdl_actual = AutoReplyModuleManager.find_one_casted({
                AutoReplyModuleModel.KEY_KW_CONTENT: kw,
                AutoReplyModuleModel.KEY_KW_TYPE: kw_type
            }, parse_cls=AutoReplyModuleModel)

            self.assertModelEqual(model, mdl_actual)

            return mdl_actual

        def _check_model_not_exists(self, model_args: dict):
            kw = model_args["Keyword"].content
            kw_type = model_args["Keyword"].content_type

            self.assertIsNone(
                AutoReplyModuleManager.find_one_casted({
                    AutoReplyModuleModel.KEY_KW_CONTENT: kw,
                    AutoReplyModuleModel.KEY_KW_TYPE: kw_type
                }, parse_cls=AutoReplyModuleModel))
