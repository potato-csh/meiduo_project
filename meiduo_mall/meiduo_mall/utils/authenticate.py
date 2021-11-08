from django.contrib.auth.backends import ModelBackend

from users.models import User


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法，实现多账号登录
        :param request:     请求对象
        :param username:    用户名
        :param password:    密码
        :param kwargs:      其他参数
        :return:
        """
        """判断前后台登录"""
        # 后台登录
        if request is None:
            try:
                # is_superuser判断是否是超级管理员
                user = User.objects.get(username=username, is_superuser=True)
            except:
                user = None
            if user is not None and user.check_password(password):
                return user
        # 前台登录
        else:
            # 变量username的值，可以是用户名，也可以是手机号，需要判断，再查询
            try:
                # if re.match(r'^1[3-9]\d{9}$', username):
                #     user = User.objects.get(mobile=username)
                # else:
                #     user = User.objects.get(username=username)
                user = User.objects.get(username=username)
            except:
                # 如果未查到数据，则返回None，用于后续判断
                try:
                    user = User.objects.get(mobile=username)
                except:
                    return None

            # 判断密码
            if user.check_password(password):
                return user
            else:
                return None
