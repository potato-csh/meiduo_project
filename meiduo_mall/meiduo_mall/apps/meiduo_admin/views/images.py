from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from fdfs_client.client import Fdfs_client

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

    # 重写拓展类的保存逻辑
    def create(self, request, *args, **kwargs):
        # 1、获取前端数据
        data = request.data
        # 2、验证数据
        ser = self.get_serializer(data=data)
        ser.is_valid()
        # 3、建⽴fastdfs的客户端
        client = Fdfs_client(settings.FASTDFS_PATH)
        file = request.FILES.get('image')
        # 4、上传图⽚
        res = client.upload_by_buffer(file.read())
        # 5、判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response({'error':'图片上传失败'})
        # 6、保存图⽚表
        img = SKUImage.objects.create(sku=ser.validated_data['sku'],image=res['Remote file_id'])
        ser.save()
        # 7、返回保存后的图⽚数据
        return Response(ser.data)