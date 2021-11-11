from rest_framework import serializers
from goods.models import SPUSpecification, SPU


class SpecsSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""

    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""

    class Meta:
        model = SPU
        fields = ('id', 'name')
