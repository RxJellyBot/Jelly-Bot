from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, RequestContext
from django.utils import timezone

from bot.system import get_boot_dt
from JellyBot import keys
from JellyBot.systemconfig import System
from JellyBot.views.nav import construct_nav
from JellyBot.api.static import result, param
from JellyBot.utils import get_root_oid
from extutils import HerokuWrapper
from extutils.flags import is_flag_class, is_flag_single, is_flag_double


def render_template(request, title, template_name, context=None, content_type=None, status=None,
                    using=None, nav_param=None) -> HttpResponse:
    if context is None:
        context = dict()
    if nav_param is None:
        nav_param = dict()

    # Append variable for base template
    context["title"] = title

    # Append navigation bar items
    nav = construct_nav(request, nav_param)
    context["nav_bar_html"] = nav.to_html()
    context["nav_bread"] = nav.to_bread()
    context["static_keys_result"] = result
    context["static_keys_param"] = param

    # Append user id vars
    context["api_token"] = request.COOKIES.get(keys.Cookies.USER_TOKEN)
    context["root_oid"] = get_root_oid(request)

    # Append version numbers for footer
    context["app_update"] = timezone.localtime(
        HerokuWrapper.latest_succeeded_release(System.HerokuAppName).updated_at).strftime("%m/%d %H:%M (UTC%z)")
    context["boot_dt"] = timezone.localtime(get_boot_dt()).strftime("%m/%d %H:%M (UTC%z)")

    # Append backend vars
    unlock_classes = []

    if get_root_oid(request):
        unlock_classes.append(keys.Css.LOGGED_IN_ENABLE)

    context["unlock_classes"] = unlock_classes

    return render(request, template_name, context, content_type, status, using)


# noinspection PyTypeChecker
def render_flag_table(request, title: str, table_title: str, flag_enum, context: dict = None,
                      content_type=None, status=None, using=None) -> HttpResponse:
    if context is None:
        context = dict()

    if not is_flag_class(flag_enum):
        raise ValueError(f"flag_enum ({type(flag_enum)}) is not the subclass of `Flag`.")

    context["has_key"] = is_flag_single(flag_enum)
    context["has_description"] = is_flag_double(flag_enum)

    context.update(**{"table_title": table_title,
                      "flags": list(flag_enum)})

    return render_template(request, title, "doc/code/generic.html", context, content_type, status, using)


def simple_str_response(request, s):
    return HttpResponse(Template("{{ result }}").render(RequestContext(request, {"result": s})))
