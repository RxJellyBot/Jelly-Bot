from datetime import timezone
from extutils import exec_timing_ns

import heroku3


class Heroku3Wrapper:
    def __init__(self):
        self._core = heroku3.from_key("83162216-3890-4b99-b5b8-ee499c06acd3")

    def apps(self):
        return self._core.apps()

    def get_app(self, app_name):
        return self.apps().get(app_name)

    def release_list(self, app_name, **kwargs):
        app = self.get_app(app_name)

        if app:
            return app.releases(**kwargs)
        else:
            return []

    def latest_succeeded_release(self, app_name, **kwargs):
        """
        Return the latest succeeded release.
        :return: `None` if no releases found.
        """
        releases = self.release_list(app_name, order_by="version", limit=1, sort="desc", **kwargs)

        if len(releases) > 0:
            return releases[0]
        else:
            return None

    def latest_success_release_str(self, app_name, tzinfo=None, strftime=None, **kwargs) -> str:
        """
        Return the summarized latest succeeded release string.
        """
        release = self.latest_succeeded_release(app_name, **kwargs)

        # FIXME: [High Priority] Make release.updated_at timezone aware. Pass tzinfo as param

        if release:
            updated_at = release.updated_at

            if tzinfo:
                updated_at = updated_at.replace(tzinfo=tzinfo)

            if strftime:
                updated_at = updated_at.strftime(strftime)

            return f"v{release.version} on {updated_at}"
        else:
            return "No latest release found."

    @property
    def rate_limit_remaining(self):
        return self._core.ratelimit_remaining()


@exec_timing_ns
def wrap():
    w = Heroku3Wrapper()
    print(w.rate_limit_remaining)
    print("JellyBotAPI")
    print(w.latest_success_release_str("jellybotapi", strftime="%m/%d %H:%M (UTC%z)"))
    print("JellyBotAPI-Staging")
    print(w.latest_success_release_str("jellybotapi-staging", strftime="%m/%d %H:%M (UTC%z)"))


@exec_timing_ns
def wrap2():
    pass


if __name__ == "__main__":
    wrap()
    wrap2()
