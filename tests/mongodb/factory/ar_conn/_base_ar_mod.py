from abc import ABC
from datetime import datetime

from bson import ObjectId

from flags import AutoReplyContentType, PermissionLevel, Platform
from models import AutoReplyContentModel, AutoReplyModuleModel, ChannelProfileModel, ChannelProfileConnectionModel
from mongodb.factory import ChannelManager
from mongodb.factory.prof import ProfileDataManager, UserProfileManager
from mongodb.factory.ar_conn import AutoReplyModuleManager

from ._base_mod_sample import TestArModuleSample

__all__ = ["TestAutoReplyModuleManagerBase"]


class TestAutoReplyModuleManagerBase(ABC):
    class TestClass(TestArModuleSample.TestClass):
        @staticmethod
        def collections_to_reset():
            return [AutoReplyModuleManager]

        def grant_access_pin_permission(self):
            reg_result = ChannelManager.ensure_register(Platform.LINE, "U123456")
            if reg_result.success:
                self.channel_oid = reg_result.model.id
            else:
                self.fail(reg_result.outcome)

            mdl = ChannelProfileModel(ChannelOid=self.channel_oid, PermissionLevel=PermissionLevel.ADMIN)
            ProfileDataManager.insert_one_model(mdl)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(
                    ChannelOid=self.channel_oid, UserOid=self.CREATOR_OID, ProfileOids=[mdl.id]))

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
