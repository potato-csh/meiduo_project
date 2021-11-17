from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from goods.models import SKU, GoodsCategory
from meiduo_admin.serializers.skus import SKUGoodsSerializer, GoodsCategorySerializer
from meiduo_admin.utils import PageNum


class SKUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SKUGoodsSerializer
    # 指定分页器
    pagination_class = PageNum

    # 重写get_query_set方法，判断是否传递keyword查询参数
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)

    # 获取下拉categories分类的信息
    @action(methods=['get'], detail=False)
    def categories(self, request):
        categories = GoodsCategory.objects.all()
        ser = GoodsCategorySerializer
