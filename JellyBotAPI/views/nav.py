from django.urls import reverse
from django.utils.translation import gettext as _

from JellyBotAPI import keys
from JellyBotAPI.components.navbar import (
    nav_items_factory, NavItemsHolder, NavEntry, NavDropdown, NavHeader, NavDivider
)


def construct_nav(request):
    current_path = request.path

    nav = NavItemsHolder()

    home_item = nav_items_factory(
        NavEntry, current_path, label=_("Home Page"), link=reverse("page.home"))
    login_item = nav_items_factory(
        NavEntry, current_path, label=_("Login"), link=reverse("page.login"), parent=home_item)
    my_account_item = nav_items_factory(
        NavEntry, current_path, label=_("My Account"), link=reverse("account.main"), parent=home_item)

    about_item = nav_items_factory(
        NavEntry, current_path, label=_("About"), link=reverse("page.about"), parent=home_item)

    auto_reply_parent = nav_items_factory(
        NavDropdown, current_path, label=_("Auto Reply"), parent=home_item)
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

    nav.add_item(home_item)

    if keys.USER_TOKEN in request.COOKIES:
        nav.add_item(my_account_item)
    else:
        nav.add_item(login_item)

    nav.add_item(auto_reply_parent)
    nav.add_item(about_item)

    return nav
