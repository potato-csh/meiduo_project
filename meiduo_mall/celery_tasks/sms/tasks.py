"""定义任务"""
from .hywx.sms2 import send_sms
from celery_tasks.main import celery_app


# 使用装饰器装饰异步任务，保证celery识别任务
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码
    :param mobile:手机号码
    :param sms_code:短信验证码
    :return: 成功：0 或者 失败：-1
    """
    send_ret = send_sms(mobile, sms_code)
    return send_ret
