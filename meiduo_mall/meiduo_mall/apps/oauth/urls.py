from django.conf.urls import url
from .views import *

urlpatterns = [
    # 提供QQ登录扫码页面
    url(r'^/qq/login/$', QQAuthURLView.as_view())
]
