import json
import pprint

import django
from django.test import Client, TestCase


c = Client(enforce_csrf_checks=True)
django.setup()


class GetJsonResponseMixin(TestCase):
    def print_and_get_json(self, http_method, url, data, print_title=None):
        if http_method.upper() == "GET":
            response = c.get(url, data)
        elif http_method.upper() == "POST":
            response = c.post(url, data)
        else:
            raise ValueError(f"Unknown HTTP method. ({http_method})")

        self.assertEqual(200, response.status_code)
        result = json.loads(response.content.decode())
        if print_title:
            print(f"===== {print_title} =====")
        pprint.pprint(result)
        print()

        return result
