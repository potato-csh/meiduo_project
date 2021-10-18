import os
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View
from alipay import AliPay

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo


class PaymentView(LoginRequiredJSONMixin, View):
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

        app_private_key_string = open(r"C:\Users\Potato\PycharmProjects\Working\meiduo_project\meiduo_mall\meiduo_mall\apps\payment\keys\app_private_key.pem").read()
        alipay_public_key_string = open(r"C:\Users\Potato\PycharmProjects\Working\meiduo_project\meiduo_mall\meiduo_mall\apps\payment\keys\alipay_public_key.pem").read()

        alipay = AliPay(
            appid="",
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA",  # RSA 或者 RSA2
            debug=False,  # 默认 False
            # verbose=False,  # 输出调试数据
            # config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )


        # 创建对接支付宝接口的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            # /Users/chao/Desktop/meiduo_30/meiduo_mall/meiduo_mall/apps/payment/views.py
            # /Users/chao/Desktop/meiduo_30/meiduo_mall/meiduo_mall/apps/payment/keys/app_private_key.pem
            app_private_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'keys\\app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'keys\\alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
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

        alipay_url = settings.ALIPAY_RETURN_URL + '?' + order_string
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
