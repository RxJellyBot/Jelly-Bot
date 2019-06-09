from django.urls import path

from .code import InsertOutcomeCodeView, GetOutcomeCodeView, OperationOutcomeCodeView

urlpatterns = [
    path('outcome/insert', InsertOutcomeCodeView.as_view(), name="page.doc.code.insert"),
    path('outcome/get', GetOutcomeCodeView.as_view(), name="page.doc.code.get"),
    path('outcome/ops', OperationOutcomeCodeView.as_view(), name="page.doc.code.ops")
]
