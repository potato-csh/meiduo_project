from django.conf.urls import url
from .views import *

urlpatterns = [
    # 注册
    url(r'^register/$', RegisterView.as_view(), name='register'),
    # 判断用户名是否重复注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', UsernameCountView.as_view()),
    # 判断手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', MobileCountView.as_view()),

    # 登录
    url(r'^login/$', LoginView.as_view(), name='login'),
    # 退出登录
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', UserInfoView.as_view(), name='info'),
    # 添加邮箱
    url(r'^emails/$', EmailView.as_view()),
    # 验证邮箱
    url(r'^emails/verification/$', VerifyEmailView.as_view()),
    # 展现收货地址
    url(r'^addresses$', AddressView.as_view(), name='address'),
    # 新增收货地址
    url(r'^addresses/create/$', AddressCreateView.as_view()),
    # 更新和删除收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', UpdateDestroyAddressView.as_view()),
    # 设置为默认收货地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', DefaultAddressView.as_view()),

]
