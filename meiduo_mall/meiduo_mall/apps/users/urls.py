from django.conf.urls import url
from .views import *

urlpatterns = [
    # 注册
    url(r'^register/$', RegisterView.as_view(), name='register'),
    # 判断用户名是否重复注册
    url(r'/usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',UsernameCountView.as_view()),
    # 判断手机号是否重复
    url(r'/mobiles/(?P<mobile>1[3-9]\d{9})/count/$',MobileCountView.as_view()),

]
