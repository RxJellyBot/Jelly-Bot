"""Helpers to integrate the process on controlling profiles."""
from dataclasses import dataclass
from typing import List, Set, Optional

from bson import ObjectId

from flags import ProfilePermission, PermissionLevel
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.helper import IdentitySearcher
from models import ChannelProfileModel


@dataclass
class ProfileControlEntry:
    """Single entry representing the profile control checking result."""

    root_oid: ObjectId
    name: str
    controllable: bool


@dataclass
class ChannelProfileEntry:
    """Single entry representing a channel profile."""

    profile: ChannelProfileModel
    owner_names: List[str]

    def __post_init__(self):
        self.owner_names = sorted(self.owner_names)


class ProfileHelper:
    """Helper to process the profile data."""

    @staticmethod
    def get_user_profile_controls(
            channel_model, profile_oid: ObjectId, requester_oid: ObjectId, permissions: Set[ProfilePermission]) \
            -> List[ProfileControlEntry]:
        """
        Check if the requester can perform certain actions on members who have the certain profile.

        The **certain actions** mentioned above currently are:

        - Control the profile attaching status

        Actions are unable to perform on the users who have a higher permission level.

        Actions also cannot be performed on default profile.

        .. note::
            This function is expensive because it calls ``IdentitySearcher.get_batch_user_name()``.

        :param channel_model: channel data of the profile
        :param profile_oid: OID of the profile
        :param requester_oid: OID of the user who requested this check
        :param permissions: permissions that the requester has
        :return: list of `ProfileControlEntry` containing the check result
        """
        ret = []

        names = IdentitySearcher.get_batch_user_name(ProfileManager.get_profile_user_oids(profile_oid), channel_model)
        perm_dict = ProfileManager.get_user_permission_lv_dict(channel_model.id)

        remove_self = ProfilePermission.PRF_CONTROL_SELF in permissions
        remove_member = ProfilePermission.PRF_CONTROL_MEMBER in permissions
        is_default = channel_model.config.default_profile_oid == profile_oid

        user_perm_lv = perm_dict.get(requester_oid, PermissionLevel.lowest())

        for uid, name in sorted(names.items(), key=lambda item: item[1]):
            if not name:
                name = str(uid)

            controllable = False
            if not is_default and user_perm_lv >= perm_dict.get(uid, PermissionLevel.lowest()):
                controllable = remove_self if uid == requester_oid else remove_member

            ret.append(ProfileControlEntry(root_oid=uid, name=name, controllable=controllable))

        return ret

    @staticmethod
    def get_channel_profiles(channel_oid: ObjectId, partial_name: Optional[str] = None) -> List[ChannelProfileEntry]:
        """
        Get a list of the channel profiles in ``channel_oid``.

        ``partial_name`` can be a part of the profile name.

        :param channel_oid: channel to get the profiles
        :param partial_name: keyword to get the profiles
        :return: list of channel profiles
        """
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
        for _, onplat_oids in user_oids_dict.items():
            user_oids.extend(onplat_oids)
        user_names = IdentitySearcher.get_batch_user_name(user_oids, channel_model)

        for prof in profs:
            uids = user_oids_dict.get(prof.id, [])

            ret.append(ChannelProfileEntry(prof, [user_names.get(uid) for uid in uids]))

        return ret
