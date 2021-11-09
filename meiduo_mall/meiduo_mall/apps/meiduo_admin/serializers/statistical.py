from rest_framework import serializers
from goods.models import GoodsVisitCount


class GoodsDayCountSerializes(serializers.ModelSerializer):
    """分类商品访问量序列化器"""

    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('count', 'category')
