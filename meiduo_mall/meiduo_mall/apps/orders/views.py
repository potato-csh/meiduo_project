import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods

from meiduo_mall.utils.views import LoginRequiredJSONMixin


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供结算订单的页面"""
        # 获取登录用户
        user = request.user

        # 查询收货地址：查询登录用户没有被逻辑删除的地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=True)
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

        total_count = 0
        total_amount = 0
        # 取出所有的skus
        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * new_cart_dict[sku.id]

            total_count += sku.count
            total_amount += sku.amount

        freight = Decimal(10.00)

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }

        # 响应结果
        return render(request, 'place_order.html', context=context)


class OrderCommitView(LoginRequiredJSONMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存订单的数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必要参数')
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否属于货到付款：1或者支付宝：2
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 当前用户
        user = request.user

        # 生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 保存订单基本信息（一）
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=0,
            freight=Decimal(10.00),
            pay_method=pay_method,
            # status = 'UNPAID' if pay_method=='ALIPAY' else 'UNSEND'
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
            OrderInfo.ORDER_STATUS_ENUM['UNSEND'],
        )

        # 获取订单商品的sku
        redis_conn = get_redis_connection('carts')
        # {b'1':b'1',b'2':b'2'}
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # [b'1']
        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        # 构造购物车中被勾选的商品的数据 {'1': '1'}
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        sku_ids = new_cart_dict.keys()
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_count = new_cart_dict[sku.id]
            # 判断SKU库存
            if sku_count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

            # 库存减少，销量增加
            sku.stock -= sku_count
            sku.sales += sku_count
            sku.save()

            # 修改SPU销量
            sku.spu.sales += sku_count
            sku.spu.save()

            # 保存订单商品信息（多）
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=sku_count,
                price=sku.price,
            )

            # 更新order里面的total_count和total_amount
            order.total_count += sku_count
            order.total_amount += (sku_count * sku.price)

        # 添加上邮费
        order.total_amount += order.freight
        order.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})
