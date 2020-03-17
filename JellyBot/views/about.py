from django.views import View
from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import System
from JellyBot.views.render import render_template
from extutils import GithubWrapper


class AboutView(View):
    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        github_commit = GithubWrapper.get_latest_commit(System.GitHubRepoIDName, System.GitHubRepoBranch)

        return render_template(request, _("About"), "about.html", {
            "commit":
                github_commit.sha,
            "commit_url":
                GithubWrapper.get_commit_url(System.GitHubRepoIDName, github_commit.sha),
            "commit_branch":
                System.GitHubRepoBranch
        })
