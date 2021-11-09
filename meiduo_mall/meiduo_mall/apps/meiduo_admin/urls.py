from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url

from .views import statistical
from .views import user

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    # ===============数据统计==================
    # 用户总数
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    # 日增用户
    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    # 日活跃用户
    url(r'^statistical/day_active/$', statistical.UserActiveCountView.as_view()),
    # 日下单用户
    url(r'^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),
    # 月增用户
    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    # 日分类商品访问量
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayCountView.as_view()),
    # ===============用户管理==================
    # 查询用户
    url(r'^users/$',user.UserView.as_view()),

]
