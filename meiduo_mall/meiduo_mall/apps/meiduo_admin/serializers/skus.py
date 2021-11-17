from rest_framework import serializers

from goods.models import SKU, SKUSpecification, GoodsCategory


class SKUGoodsSerializer(serializers.ModelSerializer):
    """sku序列化器"""

    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'


# class SKUSpecificationSerializer(serializers.ModelSerializer):
#     """sku规格表序列化器"""
#
#     class Meta:
#         model = SKUSpecification
#         fields = ()

class GoodsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'
