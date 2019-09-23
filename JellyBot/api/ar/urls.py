from django.urls import path

from .add import AutoReplyAddView, AutoReplyAddTokenActionView
from .validate import ContentValidationView
from .tag import AutoReplyTagPopularityQueryView

urlpatterns = [
    path('add', AutoReplyAddView.as_view(), name='api.ar.add'),
    path('add/token', AutoReplyAddTokenActionView.as_view(), name='api.ar.add_token'),
    path('validate', ContentValidationView.as_view(), name='api.ar.validate'),
    path('tag/pop', AutoReplyTagPopularityQueryView.as_view(), name='api.ar.tag.pop')
]
