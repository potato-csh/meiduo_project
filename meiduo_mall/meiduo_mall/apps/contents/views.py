from django.http import HttpResponse
from django.shortcuts import render
from collections import OrderedDict

# Create your views here.
from django.views import View
from contents.utils import get_categories
from contents.models import ContentCategory, Content


class IndexView(View):
    # 首页广告
    def get(self, request):
        """提供首页广告页面"""
        # 查询商品分类和频道
        categories = get_categories()

        # 查询首页广告数据
        # 查询所有的广告类别
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            # 使用广告类别查询出该类别对应的所有的广告内容
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by(
                'sequence')  # 查询出未下架的广告并排序

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)

    def post(self, requset):
        pass


