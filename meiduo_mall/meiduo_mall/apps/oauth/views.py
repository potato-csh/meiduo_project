from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings


# Create your views here.


class QQAuthURLView(View):
    """提供QQ登录页面的网站"""

    def get(self, request):
        # 接收next
        next = request.GET.get('next')

        # 创建工具(初始化对象)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()
        pass
