from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, RequestContext

from JellyBotAPI import keys
from JellyBotAPI.views.nav import construct_nav


def render_template(request, template_name, context=None, content_type=None, status=None, using=None) -> HttpResponse:
    if context is None:
        context = dict()

    # append navigation bar items
    nav = construct_nav(request)
    context["nav_bar_html"] = nav.to_html()
    context["nav_bread"] = nav.to_bread()

    # append necessary backend vars
    context["enable_if_logged_in"] = keys.ENABLE_ON_LOGGED_IN

    return render(request, template_name, context, content_type, status, using)


def simple_str_response(request, s):
    return HttpResponse(Template("{{result}}").render(RequestContext(request, {"result": s})))
