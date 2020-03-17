from dataclasses import dataclass
from typing import List

from bson import ObjectId

from flags import PermissionCategory
from mongodb.factory import ProfileManager
from mongodb.helper import IdentitySearcher


@dataclass
class ProfileControlEntry:
    root_oid: ObjectId
    name: str
    removable: bool


class ProfileHelper:
    @staticmethod
    def get_user_profile_controls(channel_model, profile_oid: ObjectId, requester_oid: ObjectId) \
            -> List[ProfileControlEntry]:
        ret = []

        names = IdentitySearcher.get_batch_user_name(
            ProfileManager.get_profile_user_oids(profile_oid), channel_model, on_not_found=None)

        permissions = ProfileManager.get_user_permissions(channel_model.id, requester_oid)
        remove_self = PermissionCategory.PRF_CONTROL_SELF in permissions
        remove_member = PermissionCategory.PRF_CONTROL_MEMBER in permissions
        is_default = channel_model.config.default_profile_oid == profile_oid

        for uid, name in sorted(names.items(), key=lambda item: item[1]):
            if not name:
                name = str(uid)

            removable = False
            if not is_default:
                if uid == requester_oid:
                    removable = remove_self
                else:
                    removable = remove_member

            ret.append(ProfileControlEntry(root_oid=uid, name=name, removable=removable))

        return ret
