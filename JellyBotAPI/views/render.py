from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, RequestContext

from JellyBotAPI import keys
from JellyBotAPI.views.nav import construct_nav
from JellyBotAPI.api.static import result, param, anchor


def render_template(request, template_name, context=None, content_type=None, status=None, using=None) -> HttpResponse:
    if context is None:
        context = dict()

    # Append navigation bar items
    nav = construct_nav(request)
    context["nav_bar_html"] = nav.to_html()
    context["nav_bread"] = nav.to_bread()
    context["static_keys_result"] = result
    context["static_keys_param"] = param
    context["static_keys_anchor"] = anchor

    # Append vars
    context["api_token"] = request.COOKIES.get(keys.USER_TOKEN)

    # Append necessary backend vars
    # INCOMPLETE: Permission: Construct an array and import here for unlocking elements
    context["unlock_classes"] = [keys.LOGGED_IN_ENABLE]

    return render(request, template_name, context, content_type, status, using)


def simple_str_response(request, s):
    return HttpResponse(Template("{{result}}").render(RequestContext(request, {"result": s})))
