"""URL conf of API v2 prototype."""
from django.urls import path

from .test import ApiV2PrototypeView

urlpatterns = [
    path('graphql', ApiV2PrototypeView.as_view(), name="apiv2proto.test"),
]
