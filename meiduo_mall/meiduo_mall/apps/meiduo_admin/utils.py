from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def jwt_response_payload_handler(token, user=None, request=None):
    """
    重写jwt返回数据方法
    :param token:
    :param user:
    :param request:
    :return:
    """
    return {
        'username': user.username,
        'id': user.id,
        'token': token
    }


class PageNum(PageNumberPagination):
    """指定分页器"""
    page_size = 5  # 后端指定每页显示数量
    page_size_query_param = 'pagesize'
    max_page_size = 20

    # 重写分页器返回对象的方法
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize', self.page_size),
        ]))
