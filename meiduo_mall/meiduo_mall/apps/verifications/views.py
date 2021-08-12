import random
import logging
from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from . import constants

from verifications.libs.captcha.captcha import captcha

from .constants import *
from .libs.hywx.sms2 import send_sms
from ...utils.response_code import RETCODE


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 生成图片验证码
        text, image = captcha.generate_captcha()

        # 保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        
        :param request: 
        :param mobile: 
        :return: JSON
        """""
        # 接受参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR})

        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')

        # 判断用户是否频繁发送短信验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})

        # 删除图像验证码，避免恶意测试图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 对比图形验证码
        image_code_server = image_code_server.decode()  # 将bytes转字符串，再比较
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入的图形验证码有误'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logging.info(sms_code)  # 手动输入日志，记录短信验证码

        # # 保存短信验证码
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # # 重新写入send_flag
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 创建管道
        p1 = redis_conn.pipline()
        # 将命令添加到队列中
        # 保存短信验证码
        p1.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送短信验证码标记
        p1.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行
        p1.execute()

        # 发送短信验证码
        send_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发短信成功'})
