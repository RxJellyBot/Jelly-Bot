from typing import List

from bson import ObjectId

from extutils.emailutils import MailSender
from extutils.checker import arg_type_ensure


class UserDataIntegrationHelper:
    @staticmethod
    @arg_type_ensure
    def integrate(old_oid: ObjectId, new_oid: ObjectId) -> bool:
        """
        :return: Integration succeed or not.
        """
        # In function import to prevent circular import
        from mongodb.factory import BaseCollection, get_collection_subclasses, MONGO_CLIENT, RootUserManager

        # Replace UID entries
        failed_names: List[str] = []

        cls: BaseCollection
        for cls in get_collection_subclasses():
            if cls.model_class:
                col = MONGO_CLIENT.get_database(cls.database_name).get_collection(cls.collection_name)
                failed_names.extend(cls.model_class.replace_uid(col, old_oid, new_oid))

        if failed_names:
            MailSender.send_email_async(
                f"Fields value replacements failed.<hr><pre>{'<br>'.join(failed_names)}</pre>",
                subject="User Data Integration Failed.")
            return False
        else:
            return RootUserManager.merge_onplat_to_api(old_oid, new_oid).is_success
