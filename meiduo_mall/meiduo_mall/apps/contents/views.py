from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    # 首页广告
    def get(self,request):
        """
        提供首页广告页面
        :param request:
        :return:
        """
        return render(request,'index.html')
    def post(self,requset):
        pass