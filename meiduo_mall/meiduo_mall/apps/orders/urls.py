from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^orders/settlement/$',OrderSettlementView.as_view(),name='settlement'),
]