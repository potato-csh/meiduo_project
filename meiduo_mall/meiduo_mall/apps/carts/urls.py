from django.conf.urls import url
from .views import *

urlpatterns = [
    # 购物车管理
    url(r'^carts/$', CartView.as_view(), name='info'),
    # 全选购物车
    url(r'^carts/selection/$', CartSelectAllView.as_view()),
    # 渲染简单购物车
    url(r'^carts/simple/$', CartSimpleView.as_view()),
]
