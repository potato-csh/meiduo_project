from rest_framework import serializers
from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    """管理员序列化器"""

    class Meta:
        model = User
        fields = "__all__"
        # 为了保证密码的安全性,添加参数,密码只能反序列化,只能写,不能读
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # 父类方法无法保存到数据库，is_staff参数为FALSE，密码为明文
    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_staff = True
        user.set_password(validated_data['password'])
        user.save()
        return user

    # 父类方法无法更新到数据库，密码为明文
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
