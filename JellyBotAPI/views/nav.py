from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _

from JellyBotAPI import keys
from JellyBotAPI.components.navbar import (
    nav_items_factory, NavItemsHolder, NavEntry, NavDropdown, NavHeader, NavDivider, NavDummy
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

    # Collect items to Nav Bar
    nav.add_item(home_item)

    if keys.Cookies.USER_TOKEN in request.COOKIES:
        nav.add_item(_construct_my_account_(current_path, home_item, nav_param))
    else:
        nav.add_item(login_item)

    nav.add_item(_construct_auto_reply_(current_path, home_item))
    nav.add_item(_construct_info_(current_path, home_item, nav_param))
    nav.add_item(_construct_docs_(current_path, home_item))
    nav.add_item(about_item)

    return nav


def _construct_my_account_(current_path, parent, nav_param):
    my_account_parent = nav_items_factory(
        NavDropdown, current_path, label=_("My Account"), parent=parent, link=reverse("account.main"))
    my_account_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Dashboard"), link=reverse("account.main"), parent=my_account_parent))
    my_account_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Settings"), link=reverse("account.settings"), parent=my_account_parent))

    # Dummy Items
    my_account_parent.add_item(nav_items_factory(
        NavDummy, current_path, label=_("Channel Registration"),
        link=reverse("account.channel.connect"), parent=my_account_parent))
    my_account_parent.add_item(nav_items_factory(
        NavDummy, current_path, label=_("Channel List"),
        link=reverse("account.channel.list"), parent=my_account_parent))
    try:
        my_account_parent.add_item(nav_items_factory(
            NavDummy, current_path, label=_("Channel Management"),
            link=reverse("account.channel.manage", kwargs=nav_param), parent=my_account_parent))
    except NoReverseMatch:
        pass

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

    # Dummy Items
    try:
        info_parent.add_item(nav_items_factory(
            NavDummy, current_path, label=_("Channel"),
            link=reverse("info.channel", kwargs=nav_param), parent=info_parent))
    except NoReverseMatch:
        pass

    try:
        info_parent.add_item(nav_items_factory(
            NavDummy, current_path, label=_("Profile Info"),
            link=reverse("info.profile", kwargs=nav_param), parent=info_parent))
    except NoReverseMatch:
        pass

    return info_parent


def _construct_docs_(current_path, parent):
    docs_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Documentation"), parent=parent)
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Terms Explanation"), link=reverse("page.doc.terms"), parent=docs_parent))
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
        NavEntry, current_path, label=_("Token Action"), link=reverse("page.doc.code.token"), parent=docs_parent))

    return docs_parent
