from rest_framework.generics import ListAPIView

from users.models import User
from ..serializers.user import UserSerializer
from ..utils import UserPageNum

class UserView(ListAPIView):
    """查询用户"""

    # 获取查询集
    queryset = User.objects.all()
    # 指定序列化器
    serializer_class = UserSerializer
    # 指定分页器
    pagination_class = UserPageNum
