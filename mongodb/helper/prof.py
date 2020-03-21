from dataclasses import dataclass
from typing import List, Set, Optional

from bson import ObjectId

from flags import ProfilePermission
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.helper import IdentitySearcher
from models import ChannelProfileModel


@dataclass
class ProfileControlEntry:
    root_oid: ObjectId
    name: str
    removable: bool


@dataclass
class ChannelProfileEntry:
    profile: ChannelProfileModel
    owner_names: List[str]

    def __post_init__(self):
        self.owner_names = sorted(self.owner_names)


class ProfileHelper:
    @staticmethod
    def get_user_profile_controls(
            channel_model, profile_oid: ObjectId, requester_oid: ObjectId, permissions: Set[ProfilePermission]) \
            -> List[ProfileControlEntry]:
        ret = []

        names = IdentitySearcher.get_batch_user_name(
            ProfileManager.get_profile_user_oids(profile_oid), channel_model, on_not_found=None)

        remove_self = ProfilePermission.PRF_CONTROL_SELF in permissions
        remove_member = ProfilePermission.PRF_CONTROL_MEMBER in permissions
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

    @staticmethod
    def get_channel_profiles(channel_oid: ObjectId, partial_name: Optional[str] = None) -> List[ChannelProfileEntry]:
        ret = []

        # Get channel profiles. Terminate if no available profiles
        profs = list(ProfileManager.get_channel_profiles(channel_oid, partial_name))
        if not profs:
            return ret

        # Get channel data. Terminate if no channel data found
        channel_model = ChannelManager.get_channel_oid(channel_oid)
        if not channel_model:
            return ret

        # Get user names, and the prof-channel dict
        user_oids_dict = ProfileManager.get_profiles_user_oids([prof.id for prof in profs])
        user_oids = []
        for k, v in user_oids_dict.items():
            user_oids.extend(v)
        user_names = IdentitySearcher.get_batch_user_name(user_oids, channel_model, on_not_found=None)

        for prof in profs:
            uids = user_oids_dict.get(prof.id, [])

            ret.append(ChannelProfileEntry(prof, [user_names.get(uid) for uid in uids]))

        return ret
