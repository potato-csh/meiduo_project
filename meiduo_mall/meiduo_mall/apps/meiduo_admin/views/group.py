from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from meiduo_admin.serializers.group import GroupSerializer
from meiduo_admin.serializers.permission import PermissionSerializer
from meiduo_admin.utils import PageNum


class GroupView(ModelViewSet):
    # 查询集
    queryset = Group.objects.all()
    # 序列化器
    serializer_class = GroupSerializer
    # 分页
    pagination_class = PageNum
    # 权限
    permission_classes = [IsAdminUser]

    # 获取下拉权限列表
    def simple(self, request):
        data = Permission.objects.all()
        ser = PermissionSerializer(data, many=True)
        return Response(ser.data)
