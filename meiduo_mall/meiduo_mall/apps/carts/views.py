import base64
import json
import pickle

from django import http
from django.shortcuts import render
from django.views import View
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

    def get(self, request):
        """展示购物车"""
        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:
            # 用户已登录，从Redis中获取数据
            conn_redis = get_redis_connection('carts')

            # 查询hash数据 {b'3': b'1'}
            redis_cart = conn_redis.hgetall('carts_%s' % user.id)
            # 查询set数据 {b'3'}
            redis_selected = conn_redis.smembers('selected_%s' % user.id)

            """
            Redis用两个类型存储购物车数据
            carts_user_id: {sku_id1: count, sku_id3: count, sku_id5: count, ...}
            selected_user_id: [sku_id1, sku_id3, ...]
            
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

            cart_dict = {}
            # 将redis_cart和redis_selected进行数据结构的构造，合并数据，数据结构跟未登录用户购物车结构一致
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 用户未登录，从Cookie中获取数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转换为
                cart_str_bytes = cart_str.encode()
                # 将cookie_cart_str转换为bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转换为真正的字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        # 构造响应数据
        # 获取字典中所有的key,(sku_id)
        sku_ids = cart_dict.keys()
        # 一次性查询出所有的skus
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus
        }

        # 响应结果
        return render(request, 'cart.html', context=context)

    def put(self, request):
        """修改购物车"""
        # 接受参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)  # 可选

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:
            # 若用户登录，Redis
            conn_redis = get_redis_connection('carts')
            pl = conn_redis.pipeline()
            # 因为接口设计为幂等的，直接覆盖
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 判断商品是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()

            # 构造响应数据
            cart_sku = {
                'id': sku.id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})

        else:
            # 若用户未登录，Cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'select': sku_id
            }

            # 返回结果，为保存到cookie中
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 构造响应数据
            cart_sku = {
                'id': sku.id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str, max_age=3600)
            # 响应结果
            return response

    def delete(self, request):
        """删除购物车"""
        # 接受参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:
            # 用户已登录，Redis
            conn_redis = get_redis_connection('carts')
            pl = conn_redis.pipeline()
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '商品删除成功'})

        else:
            # 用户未登录，Cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '商品删除成功'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart_str, max_age=3600)
                # 响应结果
                return response


class CartSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        # 获取参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        # 判断用户是否登录
        if user is not None and user.is_authenticated:
            # 用户已登录，Redis
            conn_redis = get_redis_connection('carts')
            cart = conn_redis.hgetall('cart_%s' % user.id)
            sku_id_list = cart.keys()
            # 判断是否全选
            if selected:
                # 全选
                # *sku_id_list前面的*代表着添加的是列表，若为字典可以**sku_id_dict
                conn_redis.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                conn_redis.srem('selected_%s' % user.id, *sku_id_list)

            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})

        else:
            # 用户未登录，Cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart_str, max_age=3600)
            # 返回响应
            return response


class CartSimpleView(View):
    """渲染简单购物车"""

    def get(self, request):
        """
            carts_user_id: {sku_id1: count, sku_id3: count, sku_id5: count, ...}
            selected_user_id: [sku_id1, sku_id3, ...]
           
                       ||
                       ||
                       \/
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
        user = request.user
        # 判断用户是否登录
        if user.is_authenticated:
            # 用户已登录，查询Redis数据
            conn_redis = get_redis_connection('carts')
            redis_cart = conn_redis.hgetall('carts_%s' % user.id)
            redis_selected = conn_redis.smembers('selected_%s' % user.id)
            cart_dict = {}
            # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 用户未登录，查询cookie数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 构造json数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict[sku.id].get('count'),
                'default_image_url': sku.default_image.url
            })

        """
           {
               "code":"0",
               "errmsg":"OK",
               "cart_skus":[
                   {
                       "id":1,
                       "name":"Apple MacBook Pro 13.3英寸笔记本 银色",
                       "count":1,
                       "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429"
                   },
                   ......
               ]
           }
        """
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})
