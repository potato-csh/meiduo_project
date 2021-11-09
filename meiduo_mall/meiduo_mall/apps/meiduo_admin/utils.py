from rest_framework.pagination import PageNumberPagination


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


class UserPageNum(PageNumberPagination):
    """指定分页器"""