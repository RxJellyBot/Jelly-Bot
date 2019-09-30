from typing import List

from bson import ObjectId

from extutils.emailutils import MailSender
from models.field import BaseField
from mongodb.factory import BaseCollection, get_collection_subclasses, MONGO_CLIENT, RootUserManager


class UserIdentityIntegrationHelper:
    @staticmethod
    def integrate(src_root_oid: ObjectId, dest_root_oid: ObjectId) -> bool:
        """
        :return: Integration succeed or not.
        """
        # Replace UID entries
        failed_names: List[str] = []

        cls: BaseCollection
        for cls in get_collection_subclasses():
            if cls.model_class:
                col = MONGO_CLIENT.get_database(cls.database_name).get_collection(cls.collection_name)

                for k in cls.model_class.model_fields():
                    fd: BaseField = getattr(cls.model_class, k, None)
                    if fd.stores_uid:
                        result = fd.replace_uid(col, src_root_oid, dest_root_oid)
                        if not result:
                            failed_names.append(fd.__class__.__qualname__)

        if failed_names:
            MailSender.send_email_async(
                f"Fields value replacements failed.<hr><pre>{'<br>'.join(failed_names)}</pre>",
                subject="User Identity Integration Failed.")
            return False
        else:
            return RootUserManager.remove_root_user(src_root_oid)
