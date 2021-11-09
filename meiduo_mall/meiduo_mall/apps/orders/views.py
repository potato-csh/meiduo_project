import json
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django import http
from django.db import transaction
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
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            # 如果没有查询出地址，则跳转到地址编辑页面
            addresses = None

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

        # 明显的开启一次事务
        with transaction.atomic():
            # 在数据库操作之前需要指定保存点（保存数据库最初的状态）
            save_id = transaction.savepoint()

            # 暴力回滚
            try:
                # 当前用户
                user = request.user

                # 生成订单编号：年月日时分秒+用户编号
                order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

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
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
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

                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        sku_count = new_cart_dict[sku.id]

                        # 原始数据
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断SKU库存
                        if sku_count > origin_stock:
                            # 库存不足，回滚到保存点
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # # 模拟网络延迟
                        # import time
                        # time.sleep(7)

                        # # 库存减少，销量增加
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        if result == 0:
                            continue

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

                        # 下单成功或者失败就跳出循环
                        break

                # 添加上邮费
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                # 事务回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_id)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context=context)


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request, page_num):
        """提供我的订单页面"""

        # 查询当前用户
        user = request.user
        # 查询所有订单
        orders = user.orderinfo_set.all().order_by('-create_time')
        # 遍历所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定订单支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.sku_list = []
            # 查询该订单的商品
            order_goods = order.skus.all()
            # 遍历该订单的商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        page_num = int(page_num)
        # 分页
        if orders:
            paginator = Paginator(orders, 5)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        else:
            return http.HttpResponseNotFound('订单不存在')

        # 响应结果
        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'user_center_order.html', context=context)


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """展示商品评价页面"""
        # 获取参数
        order_id = request.GET.get('order_id')

        # 检验参数
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        # 查询订单中未被评价的商品信息
        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception as e:
            return http.HttpResponseForbidden('商品信息错误')

        # 构造待评价商品数据
        skus = []
        for good in uncomment_goods:
            skus.append({
                'order_id': order_id,
                'sku_id': good.sku.id,
                'name': good.sku.name,
                'price': str(good.sku.price),
                'default_image_url': good.sku.default_image.url,
                'comment': good.comment,
                'score': good.score,
                'is_anonymous': str(good.is_anonymous)
            })

        context = {
            'skus': skus
        }

        # 返回响应
        return render(request, 'goods_judge.html', context=context)

    def post(self, request):
        """评价订单商品页面"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')

        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(order_id=order_id, user=request.user,
                                     status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')

        # 保存评价信息
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
            comment=comment,
            score=score,
            is_anonymous=is_anonymous,
            is_commented=True
        )

        # 累计评价数据
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # 如果所有订单商品都已评价，则修改订单状态为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})


class GoodsCommentView(View):
    """订单商品评价信息"""

    def get(self, request, sku_id):
        # 获取被评价的订单商品信息
        """
        {
            "code":"0",
            "errmsg":"OK",
            "comment_list":[
                {
                    "username":"itcast",
                    "comment":"这是一个好手机！",
                    "score":4
                }
            ]
        }
        """
        # 获取已评价商品的评论信息
        order_goods_list = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)
        # 序列化
        comment_list = []
        for goods in order_goods_list:
            username = goods.order.user.username
            comment_list.append({
                'username': username,
                'comment': goods.comment,
                'score': goods.score
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'comment_list': comment_list})
