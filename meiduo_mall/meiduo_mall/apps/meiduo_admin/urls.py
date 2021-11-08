from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url

from .views import statistical

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    # ===============数据统计==================
    # 用户总数
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    # 日增用户
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
]
