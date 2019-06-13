from django.urls import reverse
from django.utils.translation import gettext as _

from JellyBotAPI import keys
from JellyBotAPI.components.navbar import (
    nav_items_factory, NavItemsHolder, NavEntry, NavDropdown, NavHeader, NavDivider
)


def construct_nav(request):
    current_path = request.path

    nav = NavItemsHolder()

    # Construct Home Page item
    home_item = nav_items_factory(
        NavEntry, current_path, label=_("Home Page"), link=reverse("page.home"))

    # Construct Login item
    login_item = nav_items_factory(
        NavEntry, current_path, label=_("Login"), link=reverse("page.login"), parent=home_item)

    # Construct My Account item
    my_account_item = nav_items_factory(
        NavEntry, current_path, label=_("My Account"), link=reverse("account.main"), parent=home_item)

    # Construct About item
    about_item = nav_items_factory(
        NavEntry, current_path, label=_("About"), link=reverse("page.about"), parent=home_item)

    # Collect items to Nav Bar
    nav.add_item(home_item)

    if keys.USER_TOKEN in request.COOKIES:
        nav.add_item(my_account_item)
    else:
        nav.add_item(login_item)

    nav.add_item(_construct_auto_reply(current_path, home_item))
    nav.add_item(_construct_docs(current_path, home_item))
    nav.add_item(about_item)

    return nav


def _construct_auto_reply(current_path, parent):
    auto_reply_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Auto Reply"), parent=parent)
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


def _construct_docs(current_path, parent):
    docs_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Documentation"), parent=parent)
    docs_parent.add_item(nav_items_factory(
        NavHeader, label=_("Outcome Code"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Get Outcome"), link=reverse("page.doc.code.get"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Insert Outcome"), link=reverse("page.doc.code.insert"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Operation Outcome"), link=reverse("page.doc.code.ops"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavDivider, parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavHeader, label=_("Action Code"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("API Action"), link=reverse("page.doc.code.api"), parent=docs_parent))
    docs_parent.add_item(nav_items_factory(
        NavEntry, current_path, label=_("Token Action"), link=reverse("page.doc.code.token"), parent=docs_parent))

    return docs_parent
