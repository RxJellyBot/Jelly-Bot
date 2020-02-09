import requests
from dotmap import DotMap


class GitHubWrapper:
    API_URL = "https://api.github.com"

    def __init__(self):
        self._cache_deployments = {}
        self._cache_commit = {}

    # noinspection PyMethodMayBeStatic
    def get_latest_deployment(self, repoidname, environment):
        if environment not in self._cache_deployments:
            response = requests.get(f"{GitHubWrapper.API_URL}/repos/{repoidname}/deployments", {
                "environment": environment
            })

            list_ = response.json()

            if list_:
                self._cache_deployments[environment] = list_
                return DotMap(list_[0])
            else:
                return None
        else:
            return DotMap(self._cache_deployments[environment][0])

    def get_latest_commit(self, repoidname, branch):
        if branch not in self._cache_commit:
            response = requests.get(f"{GitHubWrapper.API_URL}/repos/{repoidname}/commits/{branch}").json()

            if response:
                self._cache_commit[branch] = response
                return DotMap(response)
            else:
                return None
        else:
            return DotMap(self._cache_commit[branch])

    @staticmethod
    def get_commit_url(repo_id_name: str, commit_sha: str):
        return f"https://github.com/{repo_id_name}/commit/{commit_sha}"


_inst = GitHubWrapper()
