from dateutil import parser

from django.utils.timezone import localtime
from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.sysconfig import System
from JellyBot.views.render import render_template
from extutils import HerokuWrapper, GithubWrapper


class AboutView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return render_template(request, _("About"), "about.html", {
            "beta_update_about": localtime(
                HerokuWrapper.latest_succeeded_release(
                    System.HerokuAppNameBeta).updated_at).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "stable_update_about": localtime(
                HerokuWrapper.latest_succeeded_release(
                    System.HerokuAppNameStable).updated_at).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "beta_deploy": localtime(
                parser.parse(
                    GithubWrapper.get_latest_deployment(
                        System.HerokuAppNameBeta).updated_at)).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "stable_deploy": localtime(
                parser.parse(
                    GithubWrapper.get_latest_deployment(
                        System.HerokuAppNameStable).updated_at)).strftime("%m/%d %H:%M:%S (UTC%z)")
        })
