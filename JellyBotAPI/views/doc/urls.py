from django.urls import path

from .code import (
    InsertOutcomeCodeView, GetOutcomeCodeView, OperationOutcomeCodeView,
    APIActionCodeView, TokenActionCodeView
)

urlpatterns = [
    path('outcome/insert', InsertOutcomeCodeView.as_view(), name="page.doc.code.insert"),
    path('outcome/get', GetOutcomeCodeView.as_view(), name="page.doc.code.get"),
    path('outcome/ops', OperationOutcomeCodeView.as_view(), name="page.doc.code.ops"),
    path('action/api', APIActionCodeView.as_view(), name="page.doc.code.api"),
    path('action/token', TokenActionCodeView.as_view(), name="page.doc.code.token")
]
