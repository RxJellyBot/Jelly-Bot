from bson import ObjectId

from models.field import BaseField
from mongodb.factory import BaseCollection, collection_sub_classes, MONGO_CLIENT


class UserIdentityIntegrationHelper:
    @staticmethod
    def integrate(src_root_oid: ObjectId, dest_root_oid: ObjectId):
        cls: BaseCollection
        for cls in collection_sub_classes():
            if cls.model_class:
                col = MONGO_CLIENT.get_database(cls.database_name).get_collection(cls.collection_name)

                for k in cls.model_class.model_fields():
                    fd: BaseField = getattr(cls.model_class, k, None)
                    if fd.stores_uid:
                        fd.replace_uid(col, dest_root_oid, src_root_oid)

        # FIXME: [SHP] This function - Remove old root uid entry in user.root
        # FIXME: [HP] Integrate page / process
