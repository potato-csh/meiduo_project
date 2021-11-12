from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import statistical, images
from .views import user
from .views import specs

urlpatterns = [
    #  ===============管理员登录==================
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
    # 用户管理
    url(r'^users/$', user.UserView.as_view()),
    # ===============规格表管理==================
    url(r'^goods/simple/$', specs.SpecsView.as_view({'get': 'simple'})),
    # ===============图片管理==================
    url(r'^skus/simple/$', images.ImageView.as_view({'get': 'simple'})),

]

# ===============规格表管理==================
router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, basename='specs')

# ===============图片管理==================
router.register('skus/images',images.ImageView,basename='images')

print(router.urls)
urlpatterns += router.urls



