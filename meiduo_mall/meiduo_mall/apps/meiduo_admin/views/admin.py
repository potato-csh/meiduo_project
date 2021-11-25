from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group
from rest_framework.response import Response

from meiduo_admin.serializers.admin import AdminSerializer
from meiduo_admin.serializers.group import GroupSerializer
from meiduo_admin.utils import PageNum
from users.models import User


class AdminView(ModelViewSet):
    # 查询集
    queryset = User.objects.filter(is_staff=True)
    # 序列化器
    serializer_class = AdminSerializer
    # 分页
    pagination_class = PageNum
    # 权限
    permission_classes = [IsAdminUser]

    # 获取下拉用户组列表
    def simple(self, request):
        data = Group.objects.all()
        ser = GroupSerializer(data, many=True)
        return Response(ser.data)
