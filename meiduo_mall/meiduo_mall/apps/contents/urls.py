from django.conf.urls import url
from .views import *

urlpatterns = {
    # 首页广告
    url(r'^$', IndexView.as_view(), name='index')
}
