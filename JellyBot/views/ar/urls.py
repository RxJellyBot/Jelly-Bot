from django.urls import path

from .add import AutoReplyAddView
from .ranking import AutoReplyRankingChannelView, AutoReplyRankingChannelListView
from .search import AutoReplySearchChannelListView, AutoReplySearchChannelView
from .main import MainPageView

urlpatterns = [
    path('', MainPageView.as_view(), name="page.ar.main"),
    path('add/', AutoReplyAddView.as_view(), name="page.ar.add"),
    path('ranking/<str:channel_oid>', AutoReplyRankingChannelView.as_view(), name="page.ar.ranking.channel"),
    path('ranking/', AutoReplyRankingChannelListView.as_view(), name="page.ar.ranking.list"),
    path('search/<str:channel_oid>', AutoReplySearchChannelView.as_view(), name="page.ar.search.channel"),
    path('search/', AutoReplySearchChannelListView.as_view(), name="page.ar.search.list")
]
