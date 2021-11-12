from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.images import ImageSerializer, SKUSerializer
from meiduo_admin.utils import PageNum


class ImageView(ModelViewSet):
    # 指定查询集
    queryset = SKUImage.objects.all()
    # 指定序列化器
    serializer_class = ImageSerializer
    # 指定分页器
    pagination_class = PageNum

    def simple(self, request):
        """获取sku商品id"""
        skus = SKU.objects.all()
        ser = SKUSerializer(skus,many=True)
        return Response(ser.data)
