from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from .models import User
from .constants import VERIFY_EMAIL_TOKEN_EXPIRES


def check_verify_email_token(token):
    """
    验证token并提取user
    :param token:序列化后的用户信息
    :return:user
    """
    s = Serializer(settings.SECRET_KEY, VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = s.loads(token)
    except BadData:
        return None
    else:
        # 从data中取出username和email
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    """
    生成验证邮箱的路径
    :param user:当前登录用户
    :return:
    http://www.meiduo.site:8000/emails/verification/?token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTU1ODA2MDE0MSwiZXhwIjoxNTU4MTQ2NTQxfQ.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InpoYW5namllc2hhcnBAMTYzLmNvbSJ9.y1jaafj2Mce-LDJuNjkTkVbichoq5QkfquIAhmS_Vkj6m-FLOwBxmLTKkGG0Up4eGGfkhKuI11Lti0n3G9XI3Q
    """
    # 初始化序列化对象
    s = Serializer(settings.SECRET_KEY, VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = s.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


# def get_user_by_account(account):
#     """
#     根据account查询用户
#     :param account: 用户名或者手机号
#     :return: user
#     """
#     try:
#         if re.match('^1[3-9]\d{9}$', account):
#             # 手机号登录
#             user = User.objects.get(mobile=account)
#         else:
#             # 用户名登录
#             user = User.objects.get(username=account)
#     except User.DoesNotExist:
#         return None
#     else:
#         return user


# class UsernameMobileAuthBackend(ModelBackend):
#     """自定义用户认证后端"""
#
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         """
#         重写认证方法，实现多账号登录
#         :param request:     请求对象
#         :param username:    用户名
#         :param password:    密码
#         :param kwargs:      其他参数
#         :return:
#         """
#
#         # 根据传入的username获取user对象。username可以是手机号也可以是用户名
#         user = get_user_by_account(username)
#         # 校验user是否存在并校验密码是否正确
#         if user and user.check_password(password):
#             return user


