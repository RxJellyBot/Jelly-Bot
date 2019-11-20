from django.urls import path

from .add import AutoReplyAddView, AutoReplyAddExecodeView
from .validate import ContentValidationView
from .tag import AutoReplyTagPopularityQueryView

urlpatterns = [
    path('add', AutoReplyAddView.as_view(), name='api.ar.add'),
    path('add/execode', AutoReplyAddExecodeView.as_view(), name='api.ar.add_execode'),
    path('validate', ContentValidationView.as_view(), name='api.ar.validate'),
    path('tag/pop', AutoReplyTagPopularityQueryView.as_view(), name='api.ar.tag.pop')
]
