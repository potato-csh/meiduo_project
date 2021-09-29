from django.conf.urls import url
from .views import *

urlpatterns = [
    # 购物车管理
    url(r'^carts/$', CartView.as_view(), name='carts'),
]
