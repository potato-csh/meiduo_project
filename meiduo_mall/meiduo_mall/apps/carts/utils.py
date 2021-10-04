import json, pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    3.1 Redis数据库中的购物车数据保留。
    3.2 如果cookie中的购物车数据在Redis数据库中已存在，将cookie购物车数据覆盖Redis购物车数据。
    3.3 如果cookie中的购物车数据在Redis数据库中不存在，将cookie购物车数据新增到Redis。
    3.4 最终购物车的勾选状态以cookie购物车勾选状态为准。

    合并购物车
    :param request:本次请求对象，获取cookie
    :param response:本次响应对象，清除cookie中的数据
    :param user:登录用户信息，获取user_id
    :return:
    """
    # 获取参数
    cart_str = request.COOKIES.get('carts')
    # 若cookie中没有响应的数据
    if not cart_str:
        return response

    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    """
    {
        "sku_id1":{
            "count":"1",
            "selected":"True"
        },
        "sku_id3":{
            "count":"3",
            "selected":"True"
        }
    }
                ||
                ||
                \/
                
    carts_user_id: {sku_id1: count, sku_id3: count, sku_id5: count, ...}
    selected_user_id: [sku_id1, sku_id3, ...]
    """

    new_carts_dict = {}
    new_selected_add = []
    new_selected_rem = []

    for sku_id, cookie_dict in cart_dict.items():
        # 构造new_cart_dict
        new_carts_dict[sku_id] = cookie_dict['count']
        # 构造new_selected_add和new_selected_rem
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # 将数据保存到cookie中
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    pl.hmset('carts_%s' % user.id, new_carts_dict)
    # 将勾选状态同步到redis数据库
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    # 清除cookie
    response.delete_cookie('carts')

    # 返回响应
    return response
