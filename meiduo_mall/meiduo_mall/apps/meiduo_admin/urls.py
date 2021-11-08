from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url

from .views import statistical


urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    # ===============数据统计==================
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
]
