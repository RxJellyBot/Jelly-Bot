from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, RequestContext
from django.utils import timezone

from bot.system import boot_dt_utc
from JellyBot import keys
from JellyBot.systemconfig import System
from JellyBot.views.nav import construct_nav
from JellyBot.api.static import result, param
from JellyBot.utils import get_root_oid
from extutils import HerokuWrapper
from extutils.flags import FlagCodeMixin, FlagSingleMixin, FlagDoubleMixin


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
    context["boot_dt"] = timezone.localtime(boot_dt_utc).strftime("%m/%d %H:%M (UTC%z)")

    # Append backend vars
    unlock_classes = []

    if get_root_oid(request):
        unlock_classes.append(keys.Css.LOGGED_IN_ENABLE)

    context["unlock_classes"] = unlock_classes

    return render(request, template_name, context, content_type, status, using)


# noinspection PyTypeChecker
def render_flag_table(request, title: str, table_title: str, flag_enum: type(FlagCodeMixin), context: dict = None,
                      content_type=None, status=None, using=None) -> HttpResponse:
    if context is None:
        context = dict()

    if not issubclass(flag_enum, FlagCodeMixin):
        raise ValueError(f"flag_enum ({flag_enum}) is not the subclass of `Flag`.")

    context["has_key"] = issubclass(flag_enum, FlagSingleMixin)
    context["has_description"] = issubclass(flag_enum, FlagDoubleMixin)

    context.update(**{"table_title": table_title,
                      "flags": list(flag_enum)})

    return render_template(request, title, "doc/code/generic.html", context, content_type, status, using)


def simple_str_response(request, s):
    return HttpResponse(Template("{{ result }}").render(RequestContext(request, {"result": s})))
