from django.conf.urls import url
from .views import *

urlpatterns = [
    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', ListViews.as_view(), name='list'),
    # 热销排行
    url(r'^hot/(?P<category_id>\d+)/$', HotGoodsView.as_view()),
    # 商品详情页
    url(r'^detail/(?P<sku_id>\d+)/$', DetailView.as_view(), name='detail'),
    # 分类商品访问量
    url(r'^detail/visit/(?P<category_id>\d+)/$',DetailVisitView.as_view())
]
