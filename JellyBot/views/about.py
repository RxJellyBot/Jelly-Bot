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
        github_beta_deploy = GithubWrapper.get_latest_deployment(System.GitHubRepoIDName, System.HerokuAppNameBeta)
        github_stable_deploy = GithubWrapper.get_latest_deployment(System.GitHubRepoIDName, System.HerokuAppNameStable)

        return render_template(request, _("About"), "about.html", {
            "beta_update_about": localtime(
                HerokuWrapper.latest_succeeded_release(
                    System.HerokuAppNameBeta).updated_at).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "stable_update_about": localtime(
                HerokuWrapper.latest_succeeded_release(
                    System.HerokuAppNameStable).updated_at).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "beta_deploy":
                localtime(parser.parse(github_beta_deploy.updated_at)).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "beta_commit":
                github_beta_deploy.sha,
            "beta_commit_url":
                GithubWrapper.get_commit_url(System.GitHubRepoIDName, github_beta_deploy.sha),
            "stable_deploy":
                localtime(parser.parse(github_stable_deploy.updated_at)).strftime("%m/%d %H:%M:%S (UTC%z)"),
            "stable_commit":
                github_stable_deploy.sha,
            "stable_commit_url":
                GithubWrapper.get_commit_url(System.GitHubRepoIDName, github_stable_deploy.sha)
        })
