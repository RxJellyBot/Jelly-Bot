from django.urls import path

from .add import AutoReplyAddView
from .ranking import AutoReplyChannelRankingView, AutoReplyRankingChannelListView
from .main import MainPageView

urlpatterns = [
    path('', MainPageView.as_view(), name="page.ar.main"),
    path('add/', AutoReplyAddView.as_view(), name="page.ar.add"),
    path('ranking/<str:channel_oid>', AutoReplyChannelRankingView.as_view(), name="page.ar.ranking.channel"),
    path('ranking/', AutoReplyRankingChannelListView.as_view(), name="page.ar.ranking.list")
]
