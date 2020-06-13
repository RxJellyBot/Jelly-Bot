from dataclasses import dataclass, field
from typing import List, Union

from bson import ObjectId
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from extutils.color import ColorFactory, Color
from flags import CommandScopeCollection, BotFeature, ProfilePermission, PermissionLevel, ProfilePermissionDefault
from JellyBot.systemconfig import HostUrl
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from models import ChannelProfileModel
from mongodb.factory.results import OperationOutcome
from mongodb.factory import ProfileManager
from mongodb.helper import ProfileHelper

from ._base import CommandNode

cmd = CommandNode(
    codes=["pf", "prof", "profile"], order_idx=250, name=_("Profile Management"),
    description=_("Controls related to profile management."))

# region Create
cmd_create = cmd.new_child_node(
    codes=["cr", "c", "n", "new"], name=_("Create"),
    description=_(
        "Create a profile and attach it to self.\n\n"
        "## Create\n\n"
        "Parameter will be applied if not specified:\n\n"
        "- Color: `{}`\n\n"
        "- Permission: `{}`\n\n"
        "- Permission Level: `{}`").format(
        ColorFactory.DEFAULT, ProfilePermission.NORMAL, PermissionLevel.NORMAL))


@dataclass
class PermissionParseResult:
    valid: List[ProfilePermission] = field(default_factory=list)  # Able to be set on the profile
    invalid: List[ProfilePermission] = field(default_factory=list)  # Unable to be set on the profile
    skipped: List[str] = field(default_factory=list)  # Unparsable strings

    @property
    def has_valid(self) -> bool:
        return len(self.valid) > 0

    @property
    def has_invalid(self) -> bool:
        return len(self.invalid) > 0

    @property
    def has_skipped(self) -> bool:
        return len(self.skipped) > 0


def _parse_name(channel_oid: ObjectId, name: str):
    if ProfileManager.is_name_available(channel_oid, name):
        return name
    else:
        return None


def _parse_color(color: Union[str, Color]):
    if isinstance(color, str):
        try:
            return ColorFactory.from_hex(color)
        except ValueError:
            return None
    elif isinstance(color, Color):
        return color
    else:
        raise TypeError()


def _parse_permission(permission: str, max_perm_lv: PermissionLevel) -> PermissionParseResult:
    result = PermissionParseResult()

    permission = permission.split(",")
    controllable_permissions = ProfilePermissionDefault.get_overridden_permissions(max_perm_lv)

    for perm in permission:
        perm = perm.strip()

        try:
            perm = ProfilePermission.cast(perm)
        except Exception:
            result.skipped.append(perm)
            continue

        if perm in controllable_permissions:
            result.valid.append(perm)
        else:
            result.invalid.append(perm)

    return result


def _parse_permission_level(perm_lv: Union[str, PermissionLevel]):
    return PermissionLevel.cast(perm_lv, silent_fail=True)


_help_name_ = _("Name of the profile.")
_help_color_ = _("HEX color code for the profile.<br>Example: `81D8D0`")
_help_permission_ = _("Permission to be granted for the profile.<br>"
                      "If multiple, use comma to separate them.<br>"
                      "Check documentation for the permission code.<br>"
                      "Example: `1,401,403`")
_help_permission_lv_ = _("Permission level of the profile.<br>"
                         "Check documentation for the permission level.<br>"
                         "Example: `0`")


@cmd_create.command_function(
    feature_flag=BotFeature.TXT_PF_CREATE, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=1,
    arg_help=[_help_name_]
)
def profile_create_name(
        e: TextMessageEventObject, name: str):
    return profile_create_internal(e, name, ColorFactory.DEFAULT, [ProfilePermission.NORMAL], PermissionLevel.NORMAL)


@cmd_create.command_function(
    feature_flag=BotFeature.TXT_PF_CREATE, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=2,
    arg_help=[_help_name_, _help_color_]
)
def profile_create_name_color(
        e: TextMessageEventObject, name: str, color: str):
    return profile_create_internal(e, name, color, [ProfilePermission.NORMAL], PermissionLevel.NORMAL)


@cmd_create.command_function(
    feature_flag=BotFeature.TXT_PF_CREATE, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=4,
    arg_help=[_help_name_, _help_color_, _help_permission_, _help_permission_lv_]
)
def profile_create_spec_all(
        e: TextMessageEventObject, name: str, color: str, permission: str, perm_lv: str):
    return profile_create_internal(e, name, color, permission, perm_lv)


# noinspection PyTypeChecker
def profile_create_internal(
        e: TextMessageEventObject, name: str, color: Union[str, Color],
        permission: Union[str, List[ProfilePermission]], perm_lv: Union[str, PermissionLevel]):
    # --- Check permission

    profiles = ProfileManager.get_user_profiles(e.channel_model.id, e.user_model.id)
    user_permissions = ProfileManager.get_permissions(profiles)

    if ProfilePermission.PRF_CED not in user_permissions:
        return [HandledMessageEventText(content=_("Insufficient permission to create profile."))]

    # --- Parse name

    prof_name = _parse_name(e.channel_oid, name)
    if not prof_name:
        return [HandledMessageEventText(content=_("The profile name `{}` is unavailable in this channel. "
                                                  "Please choose a different one.").format(name))]

    # --- Parse color

    color = _parse_color(color)
    if not color:
        return [HandledMessageEventText(
            content=_("Failed to parse color. Make sure it is in the format of `81D8D0`."))]

    # --- Parse permission level

    perm_lv = _parse_permission_level(perm_lv)
    if not perm_lv:
        return [HandledMessageEventText(
            content=_("Failed to parse permission level. Make sure it is a valid level or check the documentation."))]

    # --- Parse permission

    msg_on_hold = []
    if isinstance(permission, str):
        max_perm_lv = ProfileManager.get_highest_permission_level(profiles)

        parsed_perm = _parse_permission(permission, max_perm_lv)
        if parsed_perm.has_skipped:
            msg_on_hold.append(HandledMessageEventText(
                content=_("Strings below were skipped because it cannot be understood as permission:\n{}").format(
                    "\n".join(parsed_perm.skipped))))
        if parsed_perm.has_invalid:
            msg_on_hold.append(HandledMessageEventText(
                content=_("Permissions below were not be able to set on the profile "
                          "because your permission level is insufficient:\n{}").format(
                    "\n".join([str(p) for p in parsed_perm.invalid]))))
        if not parsed_perm.has_valid:
            return [HandledMessageEventText(content=_("Profile permission parsing failed."))] + msg_on_hold

        permission = parsed_perm.valid

    # --- Process permission

    perm_dict = {perm.code_str: perm in permission for perm in list(ProfilePermission)}

    # --- Create Model

    mdl = ChannelProfileModel(
        ChannelOid=e.channel_model.id, Name=prof_name, Color=color, Permission=perm_dict, PermissionLevel=perm_lv)
    reg_result = ProfileManager.register_new_model(e.user_model.id, mdl)

    if reg_result.success:
        return [HandledMessageEventText(content=_("Profile created and attached."))] + msg_on_hold
    else:
        return [HandledMessageEventText(content=_("Profile registration failed."))] + msg_on_hold


def _output_profile_txt(result_entries):
    entries = []
    for entry in result_entries:
        profile = entry.profile

        str_ = [f"`{profile.id}` / {profile.name} ({profile.color.color_hex})",
                _('Detail Link: {}{}').format(HostUrl, reverse('info.profile', kwargs={'profile_oid': profile.id}))]

        if entry.owner_names:
            str_.append(_("Owner: {}").format(_(', ').join(entry.owner_names)))
        else:
            str_.append(_('Nobody has this profile for now.'))

        # Force `__proxy__` to `str`
        entries.append("\n".join([str(s) for s in str_]))

    return "\n\n".join(entries)


# endregion


# region Query
cmd_query = cmd.new_child_node(
    codes=["q", "query"], name=_("Query"),
    description=_("Find profiles which name includes the provided keyword."))


@cmd_query.command_function(
    feature_flag=BotFeature.TXT_PF_QUERY, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=1,
    arg_help=[_("Keyword to be used to find the profile. Can be a part of the profile name.")]
)
def profile_query(e: TextMessageEventObject, keyword: str):
    result = ProfileHelper.get_channel_profiles(e.channel_oid, keyword)

    if not result:
        return [HandledMessageEventText(content=_("No profile with the keyword `{}` was found.").format(keyword))]

    return [HandledMessageEventText(content=_output_profile_txt(result))]


# endregion


# region List
cmd_list = cmd.new_child_node(
    codes=["l", "lst", "list"], name=_("List"),
    description=_("List all profiles in the channel."))


@cmd_list.command_function(
    feature_flag=BotFeature.TXT_PF_LIST, scope=CommandScopeCollection.GROUP_ONLY
)
def profile_list(e: TextMessageEventObject):
    result = ProfileHelper.get_channel_profiles(e.channel_oid)

    if not result:
        return [HandledMessageEventText(content=_("No profile in this channel."))]

    return [HandledMessageEventText(content=_output_profile_txt(result))]


# endregion


# region Attach
cmd_attach = cmd.new_child_node(
    codes=["a", "attach"], name=_("Attach"),
    description=_("Attach profile to either self or a member."))


def _output_attach_outcome(outcome: OperationOutcome):
    if outcome.is_success:
        return [HandledMessageEventText(content=_("Profile attached."))]
    else:
        return [
            HandledMessageEventText(
                content=_("Failed to attach the profile.\nError: `{}` - {}").format(
                    outcome.code_str, outcome.description))]


@cmd_attach.command_function(
    feature_flag=BotFeature.TXT_PF_ATTACH, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=1,
    arg_help=[_help_name_]
)
def profile_attach_self(e: TextMessageEventObject, name: str):
    return _output_attach_outcome(ProfileManager.attach_profile_name(e.channel_oid, e.user_model.id, name))


@cmd_attach.command_function(
    feature_flag=BotFeature.TXT_PF_ATTACH, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=2,
    arg_help=[_help_name_, _("The OID of the target user to be attached to the profile.")]
)
def profile_attach_member(e: TextMessageEventObject, name: str, target_oid: ObjectId):
    return _output_attach_outcome(
        ProfileManager.attach_profile_name(e.channel_oid, e.user_model.id, name, target_oid))


# endregion


# region Detach
cmd_detach = cmd.new_child_node(
    codes=["d", "dt", "detach"], name=_("Detach"),
    description=_("Detach profile from either self or a member."))


def _output_detach_outcome(outcome: OperationOutcome):
    if outcome.is_success:
        return [HandledMessageEventText(content=_("Profile detached."))]
    else:
        return [HandledMessageEventText(
            content=_("Failed to detach the profile.\nError: `{}` - {}").format(outcome.code_str,
                                                                                outcome.description))]


@cmd_detach.command_function(
    feature_flag=BotFeature.TXT_PF_DETACH, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=1,
    arg_help=[_help_name_]
)
def profile_detach_self(e: TextMessageEventObject, name: str):
    return _output_detach_outcome(ProfileManager.detach_profile_name(e.channel_oid, name, e.user_model.id))


@cmd_detach.command_function(
    feature_flag=BotFeature.TXT_PF_ATTACH, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=2,
    arg_help=[_help_name_, _("The OID of the target user to be detached from the profile.")]
)
def profile_detach_member(e: TextMessageEventObject, name: str, target_oid: ObjectId):
    return _output_detach_outcome(
        ProfileManager.detach_profile_name(e.channel_oid, name, e.user_model.id, target_oid))


# endregion


# region Delete
cmd_delete = cmd.new_child_node(
    codes=["del", "delete"], name=_("Delete"),
    description=_("Delete profile."))


@cmd_delete.command_function(
    feature_flag=BotFeature.TXT_PF_DELETE, scope=CommandScopeCollection.GROUP_ONLY,
    arg_count=1,
    arg_help=[_help_name_]
)
def profile_delete(e: TextMessageEventObject, name: str):
    # --- Check profile name
    prof = ProfileManager.get_profile_name(e.channel_oid, name)
    if not prof:
        return [HandledMessageEventText(content=_("Profile with the name `{}` not found.").format(name))]

    # --- Check permission

    profiles = ProfileManager.get_user_profiles(e.channel_model.id, e.user_model.id)
    user_permissions = ProfileManager.get_permissions(profiles)

    if ProfilePermission.PRF_CED not in user_permissions:
        return [HandledMessageEventText(content=_("Insufficient permission to delete profile."))]

    deleted = ProfileManager.delete_profile(e.channel_oid, prof.id, e.user_model.id)
    if deleted:
        return [HandledMessageEventText(content=_("Profile deleted."))]
    else:
        return [HandledMessageEventText(content=_("Failed to delete the profile."))]
# endregion
