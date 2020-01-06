from dateutil import parser

from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import System
from JellyBot.views.render import render_template
from extutils import HerokuWrapper, GithubWrapper
from extutils.dt import localtime


class AboutView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        github_deploy = GithubWrapper.get_latest_deployment(System.GitHubRepoIDName, System.HerokuAppName)

        return render_template(request, _("About"), "about.html", {
            "heroku_release_dt": localtime(
                HerokuWrapper.latest_succeeded_release(
                    System.HerokuAppName).updated_at).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "deploy":
                localtime(parser.parse(github_deploy.updated_at)).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "commit":
                github_deploy.sha,
            "commit_url":
                GithubWrapper.get_commit_url(System.GitHubRepoIDName, github_deploy.sha)
        })
