from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):
    """图像序列化器"""

    class Meta:
        model = SKUImage
        fields = ('id', 'sku', 'image')


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    class Meta:
        model = SKU
        fields = ('id', 'name')
