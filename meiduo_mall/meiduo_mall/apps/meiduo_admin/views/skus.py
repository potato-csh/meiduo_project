from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.response import Response

from goods.models import SKU, GoodsCategory, SPU
from meiduo_admin.serializers.skus import SKUSerializer, GoodsCategorySerializer, SPUSpecificationSerializer
from meiduo_admin.utils import PageNum


class SKUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SKUSerializer
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
        """
        获取商品三级分类
        :param request:
        :return:
        """
        categories = GoodsCategory.objects.filter(parent_id__gte=38)
        # categories = GoodsCategory.objects.filter(subs__id=None)
        ser = GoodsCategorySerializer(categories, many=True)
        return Response(ser.data)

    # 获取下拉spu的信息
    def specs(self, request, pk):
        """
        获取spu商品规格信息
        :param request: spu表id值
        :return:
        """
        spu = SPU.objects.get(id=pk)
        data = spu.specs.all()
        ser = SPUSpecificationSerializer(data, many=True)
        return Response(ser.data)
