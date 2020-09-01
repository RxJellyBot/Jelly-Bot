"""Implementations for integrating user data."""
from typing import List

from bson import ObjectId

from extutils.emailutils import MailSender
from extutils.checker import arg_type_ensure
from mongodb.factory.results import OperationOutcome


class UserDataIntegrationHelper:
    """Class for helping the user data integration."""

    @staticmethod
    @arg_type_ensure
    def integrate(src_oid: ObjectId, dst_oid: ObjectId) -> OperationOutcome:
        """
        Integrate the user identity from ``src_oid`` to ``dst_oid``.

        This removes the configs and the API OID bound to ``src_oid`` (if any)
        and migrate all on-platform user OIDs to ``dst_oid``.

        After this, all fields which are storing UIDs will be checked to see if they are storing ``src_oid``.

        If so, replace it with ``dst_oid``.

        Will **NOT** change the database content and **WILL** send an email report if the replacement failed.

        :param src_oid: source root user OID
        :param dst_oid: destination root user OID
        :return: outcome of the integration
        """
        # Inline import to prevent cyclic import
        # pylint: disable=import-outside-toplevel
        from mongodb.factory import (
            new_mongo_session, get_collection_subclasses, BaseCollection, RootUserManager
        )

        merge_result = RootUserManager.merge_onplat_to_api(src_oid, dst_oid)

        if not merge_result.is_success:
            return merge_result

        # Replace UID entries
        failed_names: List[str] = []

        # Get the actual `src_oid` and `dst_oid` for actual destination
        actual_src = max(src_oid, dst_oid)
        actual_dst = min(src_oid, dst_oid)

        with new_mongo_session() as session:
            session.start_transaction()

            cls: BaseCollection
            for cls in get_collection_subclasses():
                if cls.model_class:
                    failed_names.extend(cls.model_class.replace_uid(cls(), actual_src, actual_dst, session))

            if failed_names:
                session.abort_transaction()

                MailSender.send_email_async(
                    f"Fields value replacements failed.<hr><pre>{'<br>'.join(failed_names)}</pre>",
                    subject="User Data Integration Failed.")
                return OperationOutcome.X_INTEGRATION_FAILED

            session.commit_transaction()

        return OperationOutcome.O_COMPLETED
