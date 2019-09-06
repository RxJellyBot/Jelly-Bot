import os
import sys

import heroku3


class HerokuWrapper:
    def __init__(self):
        token = os.environ.get("HEROKU_API_TOKEN")
        if token:
            # noinspection PyUnresolvedReferences
            self._core = heroku3.from_key(token)
        else:
            print("Specify HEROKU_API_TOKEN in environment variables.")
            sys.exit(1)

        self._cache_release_list = {}

    def apps(self):
        return self._core.apps()

    def get_app(self, app_name):
        return self.apps().get(app_name)

    def release_list(self, app_name, **kwargs):
        if app_name not in self._cache_release_list:
            app = self.get_app(app_name)

            if app:
                ret = app.releases(**kwargs)
                self._cache_release_list[app_name] = ret
                return ret
            else:
                return []
        else:
            return self._cache_release_list[app_name]

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


_inst = HerokuWrapper()
