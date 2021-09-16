from django import http
from django.shortcuts import render
from django.views import View

from contents.models import ContentCategory


# Create your views here.

class ListViews(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        # 检验参数
        try:
            GoodCategory = ContentCategory.objects.get(id=category_id)
        except Exception as e:
            return http.HttpResponseForbidden('参数category_id错误')


        return render(request, 'list.html')
