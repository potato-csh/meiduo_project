from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')  # id默认是read_only，不支持反序列化
        # username字段增加长度限制，password字段只参与保存，不在返回给前端，增加write_only选项参数
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            },
        }

    # 重写create方法
    def create(self, validated_data):
        user = super().create(validated_data)
        # 密码加密
        user.set_password(validated_data['password'])
        user.save()
        return user
