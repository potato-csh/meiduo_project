from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from meiduo_admin.serializers.orders import OrderSerializer
from meiduo_admin.utils import PageNum
from orders.models import OrderInfo


class OrderView(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    # 重写get_query_set方法，判断是否传递keyword查询参数
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """修改订单状态"""
        # 获取订单信息
        order = OrderInfo.objects.get(order_id=pk)
        # 获取要修改的订单状态
        status = request.data.get('status')
        # 修改订单状态
        order.status = status
        order.save()
        # 返回订单
        return Response({
            'order_id': pk,
            'status': status
        })
