import requests
from dotmap import DotMap


class GitHubWrapper:
    API_URL = "https://api.github.com"

    def __init__(self):
        self._cache_deployments = {}

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


_inst = GitHubWrapper()
