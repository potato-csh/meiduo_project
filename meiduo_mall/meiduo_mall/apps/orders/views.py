from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from users.models import Address
from goods.models import SKU


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供结算订单的页面"""
        # 获取登录用户
        user = request.user

        # 查询收货地址：查询登录用户没有被逻辑删除的地址
        try:
            address = Address.objects.filter(user=user, is_deleted=True)
        except Exception as e:
            # 如果没有查询出地址，则跳转到地址编辑页面
            address = None

        # 查询redis购物车中被勾选的商品
        redis_conn = get_redis_connection('carts')
        # 查询出所有勾选和未勾选商品，{'1':'2','3':1}
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # ['1','3']
        redis_selected = redis_conn.smembers('selected_%s' % user.id)
        # 构建勾选的数据
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 获取勾选数据的sku_id
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        # 取出所有的sku

        context = {
            'address': address,
            'skus': '',
            'total_count': '',
            'total_amount': '',
            'freight': '',
            'payment_amount': '',
        }

        # 响应结果
        return render(request, 'place_order.html', context=context)
