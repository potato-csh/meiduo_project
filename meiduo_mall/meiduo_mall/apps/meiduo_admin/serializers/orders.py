from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


# 为了满足OrderGoodsSerializer的嵌套
class SKUSerializer(serializers.ModelSerializer):
    """SKU序列号器"""

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


# 为了满足OrderSerializer的嵌套
class OrderGoodsSerializer(serializers.ModelSerializer):
    """"订单商品序列号器"""

    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderSerializer(serializers.ModelSerializer):
    """订单信息序列化器"""

    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
