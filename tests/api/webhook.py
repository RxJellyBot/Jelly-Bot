from django.test import TestCase
from django.urls import reverse

from JellyBotAPI.api.static import param as p

from ._utils import GetJsonResponseMixin


class TestTextMessageHandle(GetJsonResponseMixin, TestCase):
    def test_direct(self):
        self.print_and_get_json("GET", reverse("api.webhook.direct.text"), {
            p.Message.MESSAGE: "Test"
        })
