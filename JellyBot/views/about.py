from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import System
from JellyBot.views.render import render_template
from extutils import GithubWrapper


class AboutView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        github_deploy = GithubWrapper.get_latest_deployment(System.GitHubRepoIDName, System.HerokuAppName)

        return render_template(request, _("About"), "about.html", {
            "commit":
                github_deploy.sha,
            "commit_url":
                GithubWrapper.get_commit_url(System.GitHubRepoIDName, github_deploy.sha)
        })
