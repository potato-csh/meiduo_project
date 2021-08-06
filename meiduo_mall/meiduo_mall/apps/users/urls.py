from django.conf.urls import url

from .views import *

urlpatterns = [
    # 注册
    url(r'^register/$', RegisterView.as_view(), name='register')
]
