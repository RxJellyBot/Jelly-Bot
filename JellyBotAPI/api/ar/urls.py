from django.conf.urls import url

from .add import AutoReplyAddView, AutoReplyAddTokenActionView

urlpatterns = [
    url(r'add$', AutoReplyAddView.as_view(), name='api.ar.add'),
    url(r'add/token$', AutoReplyAddTokenActionView.as_view(), name='api.ar.add_token')
]
