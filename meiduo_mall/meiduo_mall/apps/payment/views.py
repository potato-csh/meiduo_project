import os
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View
from alipay import AliPay

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo
from payment.models import Payment


class PaymentView(View):
    """订单支付功能"""

    def get(self, request, order_id):
        """
        :param order_id: 当前要支付的订单ID
        :return: JSON
        """
        user = request.user
        # 获取参数
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        app_private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys\\app_private_key.pem")
        alipay_public_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys\\alipay_public_key.pem")

        app_private_key_string = open(r'%s' % app_private_key_path).read()
        alipay_public_key_string = open(r'%s' % alipay_public_key_path).read()

        # 创建对接支付宝接口的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            # verbose=False,  # 输出调试数据
            # config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )

        # SDK对象对接支付宝支付的接口，得到登录页的地址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 订单支付金额
            subject="美多商城%s" % order_id,  # 订单标题
            return_url=settings.ALIPAY_RETURN_URL  # 同步通知的回调地址，如果不是同步通知，就不传
        )

        # 拼接完整的支付宝登录页地址
        # 电脑网站支付(正式版)，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付(开发版)，需要跳转到：https://openapi.alipaydev.com/gateway.do? + order_string

        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        # 获取到所有的查询字符串参数
        query_dict = request.GET
        # 将查询字符串参数的类型转成标准的字典类型
        data = query_dict.dict()
        # 从查询字符串参数中提取并移除 sign，不能参与签名验证
        signature = data.pop('sign')

        app_private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys\\app_private_key.pem")
        alipay_public_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys\\alipay_public_key.pem")

        app_private_key_string = open(r'%s' % app_private_key_path).read()
        alipay_public_key_string = open(r'%s' % alipay_public_key_path).read()

        # 创建对接支付宝接口的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            # verbose=False,  # 输出调试数据
            # config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )

        # 使用SDK对象，调用验通知证接口函数，得到验证结果
        success = alipay.verify(data, signature)

        # 如果验证通过，需要将支付宝的支付状态进行处理（将美多商城的订单ID和支付宝的订单ID绑定，修改订单状态）
        if success:
            # 获取美多商场订单
            order_id = data.get('out_trade_no')
            # 获取支付宝订单
            trade_id = data.get('trade_no')
            Payment.objects.create(
                # order = order
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"]).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context=context)
        else:
            return http.HttpResponseForbidden('非法请求')
