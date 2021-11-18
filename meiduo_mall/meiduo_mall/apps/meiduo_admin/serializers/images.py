from django.conf import settings
from fdfs_client.client import Fdfs_client, get_tracker_conf
from rest_framework import serializers

from celery_tasks.static_file.tasks import get_detail_html
from goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):
    """图像序列化器"""

    class Meta:
        model = SKUImage
        fields = ('id', 'sku', 'image')

    def create(self, validated_data):
        # 3、建⽴fastdfs的客户端
        tracker_path = get_tracker_conf(settings.FASTDFS_PATH)
        client = Fdfs_client(tracker_path)
        file = self.context['request'].FILES.get('image')
        # 4、上传图⽚
        res = client.upload_by_buffer(file.read())
        # 5、判断是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})
        # 6、保存图⽚表
        img = SKUImage.objects.create(sku=validated_data['sku'], image=res.get('Remote file_id').decode())

        get_detail_html.delay(img.sku.id)
        # 7、返回保存后的图⽚数据
        return img

    def update(self, instance, validated_data):
        # 3、建⽴fastdfs的客户端
        tracker_path = get_tracker_conf(settings.FASTDFS_PATH)
        client = Fdfs_client(tracker_path)
        file = self.context['request'].FILES.get('image')
        # 4、上传图⽚
        res = client.upload_by_buffer(file.read())
        # 5、判断是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})
        # 6、更新图⽚表
        instance.image = res.get('Remote file_id').decode()

        instance.save()

        get_detail_html.delay(instance.sku.id)
        # 7、返回保存后的图⽚数据
        return instance


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""



    class Meta:
        model = SKU
        fields = ('id', 'name')
