from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta

from users.models import User
from orders.models import OrderInfo
from goods.models import GoodsVisitCount
from ..serializers.statistical import GoodsDayCountSerializes


class UserTotalCountView(APIView):
    """ 用户总数统计 """

    # 指定管理员权限
    permission_class = [IsAdminUser]

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

    # 指定管理员权限
    permission_class = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        # 日增用户数量
        count = User.objects.filter(date_joined__gte=now_date).count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserActiveCountView(APIView):
    """日活跃用户统计"""

    # 指定管理员权限
    permission_class = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        count = User.objects.filter(last_login__gte=now_date).count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserOrderCountView(APIView):
    """日下单用户统计"""

    # 指定管理员权限
    permission_class = [IsAdminUser]

    def get(self, request):
        # now_date = '2021-10-19'
        now_date = date.today()

        count = OrderInfo.objects.filter(create_time__gte=now_date).count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserMonthCountView(APIView):
    """月增用户统计"""

    # 指定管理员权限
    permission_class = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # now_date = date('2021-10-29')

        # 获取当前日期一个月前的日期
        start_date = now_date - timedelta(31)

        date_list = []
        for i in range(31):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天
            cur_date = start_date + timedelta(days=i + 1)

            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)


class GoodsDayCountView(APIView):
    """日分类商品访问量"""

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取当天访问的商品分类数量信息
        data = GoodsVisitCount.objects.filter(date=now_date)
        # 序列化返回分类数量
        ser = GoodsDayCountSerializes(data, many=True)

        return Response(ser.data)
