from django.urls import path

from .add import AutoReplyAddView
from .main import MainPageView

urlpatterns = [
    path('', MainPageView.as_view(), name="page.ar.main"),
    path('add/', AutoReplyAddView.as_view(), name="page.ar.add")
]
