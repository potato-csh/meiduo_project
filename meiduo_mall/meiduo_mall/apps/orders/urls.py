from django.conf.urls import url
from .views import *

urlpatterns = [
    # 结算订单
    url(r'^orders/settlement/$', OrderSettlementView.as_view(), name='settlement'),
    # 提交订单
    url(r'^orders/commit/$', OrderCommitView.as_view()),
    # 提交订单成功
    url(r'^orders/success/$', OrderSuccessView.as_view()),
    # 我的订单
    url(r'^orders/info/(?P<page_num>\d+)/$', UserOrderInfoView.as_view(), name='info'),
    # 订单评论
    url(r'^orders/comment/$', OrderCommentView.as_view()),
    # 详情页展示评论信息
    url(r'^comments/(?P<sku_id>\d+)/$', GoodsCommentView.as_view())

]
