from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _

from JellyBot import keys
from JellyBot.components.navbar import (
    nav_items_factory, NavItemsHolder, NavEntry, NavDropdown, NavHeader, NavDivider, NavHidden
)


def construct_nav(request, nav_param):
    current_path = request.path

    nav = NavItemsHolder()

    # Construct Home Page item
    home_item = nav_items_factory(
        NavEntry, current_path, label=_("Home Page"), link=reverse("page.home"))

    # Construct Login item
    login_item = nav_items_factory(
        NavEntry, current_path, label=_("Login"), link=reverse("account.login"), parent=home_item)

    # Construct About item
    about_item = nav_items_factory(
        NavEntry, current_path, label=_("About"), link=reverse("page.about"), parent=home_item)

    # ----------------------------

    # Attach hidden item
    _attach_hidden_(nav, home_item, current_path, nav_param)

    # Collect items to Nav Bar
    nav.add_item(home_item)

    if keys.Cookies.USER_TOKEN in request.COOKIES:
        nav.add_item(_construct_my_account_(current_path, home_item, nav_param))
    else:
        nav.add_item(login_item)

    nav.add_item(_construct_auto_reply_(current_path, home_item))
    nav.add_item(_construct_info_(current_path, home_item, nav_param))
    nav.add_item(_construct_docs_(current_path, home_item, nav_param))
    nav.add_item(_construct_services_(current_path, home_item))
    nav.add_item(about_item)

    return nav


def __attach__(holder, nav_type, current_path, label, endpoint, nav_param, parent_item):
    try:
        holder.add_item(nav_items_factory(
            nav_type, current_path, label=label,
            link=reverse(endpoint, kwargs=nav_param), parent=parent_item))
    except NoReverseMatch:
        pass


def _attach_hidden_(nav, home_item, current_path, nav_param):
    # Extra Content Page
    __attach__(nav, NavHidden, current_path, _("Extra Content"), "page.extra", nav_param, home_item)

    # Account Logout
    __attach__(nav, NavHidden, current_path, _("Logout"), "account.logout", nav_param, home_item)


def _construct_my_account_(current_path, parent, nav_param):
    my_account_parent = nav_items_factory(
        NavDropdown, current_path, label=_("My Account"), parent=parent, link=reverse("account.main"))
    my_account_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Dashboard"), link=reverse("account.main"), parent=my_account_parent))
    my_account_parent.add_item(nav_items_factory(
        NavDivider, parent=my_account_parent))
    my_account_parent.add_item(nav_items_factory(
        NavHeader, label=_("Shortcut"), parent=my_account_parent))
    my_account_parent.add_item(
        nav_items_factory(
            NavEntry, current_path, label=_("Channel List"),
            link=reverse("account.channel.list"), parent=my_account_parent))
    my_account_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Settings"), link=reverse("account.settings"), parent=my_account_parent))

    # Hidden Items
    __attach__(
        my_account_parent, NavHidden, current_path, _("Channel Registration"),
        "account.channel.connect", nav_param, my_account_parent)
    __attach__(
        my_account_parent, NavHidden, current_path, _("Channel Management"),
        "account.channel.manage", nav_param, my_account_parent)
    __attach__(
        my_account_parent, NavHidden, current_path, _("Integrate Account"),
        "account.integrate", nav_param, my_account_parent)

    return my_account_parent


def _construct_auto_reply_(current_path, parent):
    auto_reply_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Auto Reply"), parent=parent, link=reverse("page.ar.main"))
    auto_reply_parent.add_item(nav_items_factory(
        NavHeader, label=_("Introduction"), parent=auto_reply_parent))
    auto_reply_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Main Intro"), link=reverse("page.ar.main"), parent=auto_reply_parent))
    auto_reply_parent.add_item(nav_items_factory(
        NavDivider, parent=auto_reply_parent))
    auto_reply_parent.add_item(nav_items_factory(
        NavHeader, label=_("Functions"), parent=auto_reply_parent))
    auto_reply_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Add"), link=reverse("page.ar.add"), parent=auto_reply_parent))

    return auto_reply_parent


def _construct_info_(current_path, parent, nav_param):
    info_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Info"), parent=parent)

    info_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Channel"), link=reverse("info.channel.search"), parent=info_parent))

    # Hidden Items
    __attach__(info_parent, NavHidden, current_path,
               _("Channel - {}").format(nav_param.get("channel_oid", "N/A")),
               "info.channel", nav_param, info_parent)
    __attach__(info_parent, NavHidden, current_path,
               _("Channel Message Stats - {}").format(nav_param.get("channel_oid", "N/A")),
               "info.channel.msgstats", nav_param, info_parent)
    __attach__(info_parent, NavHidden, current_path,
               _("Profile Info - {}").format(nav_param.get("profile_oid", "N/A")),
               "info.profile", nav_param, info_parent)
    __attach__(info_parent, NavHidden, current_path,
               _("Channel Collection Info - {}").format(nav_param.get("chcoll_oid", "N/A")),
               "info.chcoll", nav_param, info_parent)

    return info_parent


def _construct_docs_(current_path, parent, nav_param):
    docs_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Documentation"), parent=parent)

    cmd_list = nav_items_factory(
        NavEntry, current_path, label=_("Bot Commands List"), link=reverse("page.doc.botcmd.main"), parent=docs_parent)

    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Terms Explanation"), link=reverse("page.doc.terms"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavDivider, parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavHeader, label=_("Bot"), parent=docs_parent))
    docs_parent.add_item(cmd_list)
    docs_parent.add_item(nav_items_factory(
        NavDivider, parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavHeader, label=_("Outcome Code"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Get Outcome"), link=reverse("page.doc.code.get"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Insert Outcome"), link=reverse("page.doc.code.insert"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Operation Outcome"), link=reverse("page.doc.code.ops"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Update Outcome"), link=reverse("page.doc.code.update"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavDivider, parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavHeader, label=_("Action Code"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("API Command"), link=reverse("page.doc.code.api"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Execode"), link=reverse("page.doc.code.excde"), parent=docs_parent))

    # Hidden Items
    __attach__(
        docs_parent, NavHidden, current_path, _("Bot Command - {}").format(nav_param.get("code")),
        "page.doc.botcmd.cmd", nav_param, cmd_list)

    return docs_parent


def _construct_services_(current_path, parent):
    service_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Special Services"), parent=parent)
    service_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Short URL"), link=reverse("service.shorturl"), parent=service_parent))

    return service_parent
