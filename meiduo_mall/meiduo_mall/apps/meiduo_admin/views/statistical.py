from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date

from users.models import User


class UserTotalCountView(APIView):
    """ 用户总数统计 """

    # 指定管理员权限
    permission_class = IsAdminUser

    def get(self, request):
        # 获取当前时间
        now_date = date.today()
        # 获取用户总数
        count = User.objects.all().count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserDayCountView(APIView):
    """日增用户统计"""

    def get(self, request):
        now_date = date.today()

        # 日增用户数量
        count = User.objects.filter(date_joined__gte=now_date).count()

        return Response({
            'count': count,
            'data': now_date
        })
