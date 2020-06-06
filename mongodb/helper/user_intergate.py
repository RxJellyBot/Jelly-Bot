from typing import List

from bson import ObjectId

from extutils.emailutils import MailSender
from extutils.checker import arg_type_ensure
from mongodb.factory.results import OperationOutcome


class UserDataIntegrationHelper:
    @staticmethod
    @arg_type_ensure
    def integrate(old_oid: ObjectId, new_oid: ObjectId) -> OperationOutcome:
        """
        Integrate the user identity.

        Will **NOT** change the database content if the replacement failed.

        :return: outcome of the integration.
        """
        # In function import to prevent circular import
        from mongodb.factory import new_mongo_session, get_collection_subclasses, BaseCollection, RootUserManager

        merge_result = RootUserManager.merge_onplat_to_api(old_oid, new_oid)

        if not merge_result.is_success:
            return merge_result

        # Replace UID entries
        failed_names: List[str] = []

        with new_mongo_session() as session:
            session.start_transaction()

            cls: BaseCollection
            for cls in get_collection_subclasses():
                if cls.model_class:
                    failed_names.extend(cls.model_class.replace_uid(cls(), old_oid, new_oid, session))

            if failed_names:
                session.abort_transaction()

                MailSender.send_email_async(
                    f"Fields value replacements failed.<hr><pre>{'<br>'.join(failed_names)}</pre>",
                    subject="User Data Integration Failed.")
                return OperationOutcome.X_INTEGRATION_FAILED
            else:
                session.commit_transaction()

        return OperationOutcome.O_COMPLETED
