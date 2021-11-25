from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Permission, ContentType
from rest_framework.response import Response

from meiduo_admin.serializers.permission import PermissionSerializer, ContentTypeSerializer
from meiduo_admin.utils import PageNum


class PermissionView(ModelViewSet):
    # 查询集
    queryset = Permission.objects.all()
    # 序列化器
    serializer_class = PermissionSerializer
    # 分页
    pagination_class = PageNum
    # 验证
    permission_classes = [IsAdminUser]

    # 获取下拉权限类型
    def content_types(self, request):
        data = ContentType.objects.all()
        ser = ContentTypeSerializer(data, many=True)
        return Response(ser.data)
