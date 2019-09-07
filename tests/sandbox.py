from extutils import exec_timing_ns
from dateutil import parser
import requests
from dotmap import DotMap


class GitHubWrapper:
    API_URL = "https://api.github.com"

    # noinspection PyMethodMayBeStatic
    def get_latest_deployment(self, environment):
        response = requests.get(f"{GitHubWrapper.API_URL}/repos/RaenonX/Jelly-Bot-API/deployments", {
            "environment": environment
        })

        list_ = response.json()

        if list_:
            return DotMap(list_[0])
        else:
            return None


@exec_timing_ns
def wrap():
    print(parser.parse(GitHubWrapper().get_latest_deployment("jellybotapi").updated_at))


@exec_timing_ns
def wrap2():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
