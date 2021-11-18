from django.db import transaction
from rest_framework import serializers

from celery_tasks.static_file.tasks import get_detail_html
from goods.models import SKU, SKUSpecification, GoodsCategory, SpecificationOption, SPUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """sku规格表序列化器"""

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """sku序列化器"""

    # 返回关联spu表的名称和关联的分类表的名称
    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    # 返回模型类类的spu_id和category_id
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU  # SKU表中category外键关联了GoodsCategory分类表。spu外键关联了SPU商品表
        fields = '__all__'

    # @transaction.atomic()
    def create(self, validated_data):
        specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                # 保存sku表
                sku = SKU.objects.create(**validated_data)
                # 保存sku具体规格表
                for spec in specs:
                    SKUSpecification.objects.create(spec_id=spec['spec_id'], option_id=spec['option_id'], sku=sku)

            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')

            else:
                # 提交
                transaction.savepoint_commit(save_point)
                get_detail_html.delay(sku.id)

                return sku

    def update(self, instance, validated_data):
        # 获取规格信息
        specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                SKU.objects.filter(id=instance.id).update(**validated_data)
                for spec in specs:
                    SKUSpecification.objects.create(sku=instance, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('数据库错误')
            else:
                # 提交
                transaction.savepoint_commit(save_point)
                get_detail_html.delay(instance.id)
                return instance


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):
    # SPU规格序选项列化器
    class Meta:
        model = SpecificationOption
        fields = '__all__'


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""

    # 关联序列化返回SPU表数据

    options = SpecificationOptionSerializer(many=True)

    # specificationoption_set=SpecificationOption(many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'
