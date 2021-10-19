from django.conf.urls import url
from .views import *

urlpatterns = [
    # 订单支付
    url(r'^payment/(?P<order_id>\d+)/$', PaymentView.as_view()),
    # 保存订单支付结果
    url(r'^payment/status/$', PaymentStatusView.as_view()),
]
