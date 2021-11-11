from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from goods.models import SPUSpecification, SPU
from meiduo_admin.serializers.specs import SpecsSerializer, SPUSerializer
from meiduo_admin.utils import PageNum


class SpecsView(ModelViewSet):
    """商品规格的增删查改"""

    # 指定查询集
    queryset = SPUSpecification.objects.all()
    # 指定序列化器
    serializer_class = SpecsSerializer
    # 指定分页器
    pagination_class = PageNum

    def simple(self, request):
        """获取spu商品"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)
