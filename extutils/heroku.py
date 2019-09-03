import os, sys
import heroku3


class Heroku3Wrapper:
    def __init__(self):
        token = os.environ.get("HEROKU_API_TOKEN")
        if token:
            self._core = heroku3.from_key(token)
        else:
            print("Specify HEROKU_API_TOKEN in environment variables.")
            sys.exit(1)

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

    @property
    def rate_limit_remaining(self):
        return self._core.ratelimit_remaining()


_inst = Heroku3Wrapper()
