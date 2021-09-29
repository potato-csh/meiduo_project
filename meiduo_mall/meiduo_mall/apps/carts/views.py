from django.shortcuts import render
from django.views import View
from django import http
import json, base64, pickle
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""
        # 接受参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)  # 默认为True，且是可选的

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 检查sku_id是否合法
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        # 检查count是否为数字
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        # 检查seleted是否是bool类型
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:
            # 用户已登录，Redis

            # 创建链接
            conn_redis = get_redis_connection('carts')
            # 采用管道提升效率
            pl = conn_redis.pipeline()
            """
            Redis用两个类型存储购物车数据
            carts_user_id: {sku_id1: count, sku_id3: count, sku_id5: count, ...}
            selected_user_id: [sku_id1, sku_id3, ...]
            """
            # 需要以增量计算的形式保存商品数据
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 保存商品勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录，Cookie
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
            """
            # 获取cookie中的购物车数据，并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 判断当前要添加的商品在cart_dict中是否存在
            if sku_id in cart_dict:
                # 购物车已经存在，增加count的值
                orgin_count = cart_dict[sku_id]['count']
                count += orgin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cart_dict转成byte类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 将cookie_cart_dict_byte转成byte类型的str类型
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 将cookie_cart_str_byte转成cookie可存储的str类型
            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            # 将数据添加到cookie中
            response.set_cookie('carts', cookie_cart_str, max_age=3600)

            # 响应结果
            return response
            pass

        # 返回响应
