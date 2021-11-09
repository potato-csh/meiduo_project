from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Mate:
        model = User
        field = ('id', 'username', 'mobile', 'email')
