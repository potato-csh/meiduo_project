from django.conf.urls import url
from .views import *

urlpatterns = [
    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', ListViews.as_view(), name='list'),
]
