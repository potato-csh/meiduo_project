from django.conf.urls import url
from .views import *

urlpatterns = [
    # 结算订单
    url(r'^orders/settlement/$', OrderSettlementView.as_view(), name='settlement'),
    # 提交订单
    url(r'^orders/commit/$', OrderCommitView.as_view()),
    # 提交订单成功
    url(r'^orders/success/$', OrderSuccessView.as_view()),
]
