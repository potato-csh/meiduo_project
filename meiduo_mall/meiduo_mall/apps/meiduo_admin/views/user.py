from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView

from users.models import User
from ..serializers.user import UserSerializer
from ..utils import UserPageNum


class UserView(ListCreateAPIView):
    """查询用户"""

    # 指定序列化器
    serializer_class = UserSerializer
    # 指定分页器
    pagination_class = UserPageNum

    # 为了满足前端是否传入keyword而返回不同的查询结果，重写get_queryset方法
    def get_queryset(self):
        # 前端获取keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空，则返回全部数据
        if keyword is '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)
