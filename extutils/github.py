"""Module of various utilities to interact with GitHub API."""
from typing import Optional

import requests
from dotmap import DotMap


class GitHubWrapper:
    """A wrapper to interact with GitHub API."""

    API_URL = "https://api.github.com"

    def __init__(self):
        self._cache_deployments = {}
        self._cache_commit = {}

    def get_latest_deployment(self, repo_id_name, environment) -> Optional[DotMap]:
        """
        Get the latest deployment data from GitHub API.

        ``repo_id_name`` needs to be in the format of ``{USER_NAME}/{REPO_NAME}``.
        For example: ``RxJellyBot/Jelly-Bot``.

        Returns ``None`` if not found.

        Note that the result will be cached and it will only be deleted when the application exits.

        :param repo_id_name: id and the name of the repo to get
        :param environment: name of the environment of the deployment
        :return: a `DotMap` for the latest deployment data
        """
        if environment in self._cache_deployments:
            return DotMap(self._cache_deployments[environment][0])

        response = requests.get(f"{GitHubWrapper.API_URL}/repos/{repo_id_name}/deployments", {
            "environment": environment
        })

        list_ = response.json()

        if not list_:
            return None

        self._cache_deployments[environment] = list_
        return DotMap(list_[0])

    def get_latest_commit(self, repo_id_name, branch) -> Optional[DotMap]:
        """
        Get the latest commit data from GitHub API.

        ``repo_id_name`` needs to be in the format of ``{USER_NAME}/{REPO_NAME}``.
        For example: ``RxJellyBot/Jelly-Bot``.

        Returns ``None`` if not found.

        Note that the result will be cached and it will only be deleted when the application exits.

        :param repo_id_name: id and the name of the repo to get
        :param branch: name of the branch to get the commit
        :return: a `DotMap` for the latest deployment data
        """
        if branch in self._cache_commit:
            return DotMap(self._cache_commit[branch])

        response = requests.get(f"{GitHubWrapper.API_URL}/repos/{repo_id_name}/commits/{branch}").json()

        if not response:
            return None

        self._cache_commit[branch] = response
        return DotMap(response)

    @staticmethod
    def get_commit_url(repo_id_name: str, commit_sha: str):
        """
        Get the URL of a commit. This method won't fail as it simply combines the arguments and generate an URL.

        ``repo_id_name`` needs to be in the format of ``{USER_NAME}/{REPO_NAME}``.
        For example: ``RxJellyBot/Jelly-Bot``.

        :param repo_id_name: id and the name of the repo to get
        :param commit_sha: hash of the commit
        :return: URL of the corresponding commit
        """
        return f"https://github.com/{repo_id_name}/commit/{commit_sha}"


_inst = GitHubWrapper()
