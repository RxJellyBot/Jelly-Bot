from django.urls import path

from .code import (
    InsertOutcomeCodeView, GetOutcomeCodeView, OperationOutcomeCodeView, UpdateOutcomeCodeView,
    APIActionCodeView, TokenActionCodeView
)
from .main import TermsExplanationView

urlpatterns = [
    path('terms', TermsExplanationView.as_view(), name="page.doc.terms"),
    path('outcome/insert', InsertOutcomeCodeView.as_view(), name="page.doc.code.insert"),
    path('outcome/get', GetOutcomeCodeView.as_view(), name="page.doc.code.get"),
    path('outcome/account', OperationOutcomeCodeView.as_view(), name="page.doc.code.ops"),
    path('outcome/upd', UpdateOutcomeCodeView.as_view(), name="page.doc.code.update"),
    path('action/api', APIActionCodeView.as_view(), name="page.doc.code.api"),
    path('action/token', TokenActionCodeView.as_view(), name="page.doc.code.token")
]
