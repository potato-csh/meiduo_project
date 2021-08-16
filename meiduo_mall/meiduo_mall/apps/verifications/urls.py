from django.conf.urls import url

from .views import *


urlpatterns = [
    # 图形验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', ImageCodeView.as_view()),
    # 短信验证码
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', SMSCodeView.as_view()),
]
