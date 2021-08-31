from django.shortcuts import render
from django.views import View
from django import http
from users.models import User
from areas.models import Area
import logging
from django.core.cache import cache

from meiduo_mall.utils.response_code import RETCODE

# 创建日志生成器
logger = logging.getLogger('django')


class AreaView(View):
    """省市区三级联动"""

    def get(self, request):
        # 判断当前是要查询省份数据还是市区数据
        area_id = request.GET.get('area_id')
        if not area_id:
            # 查询的是省份数据

            # 获取并判断是否有缓存
            province_list = cache.get('province_list')

            if not province_list:
                try:
                    # Area.objects.filter(属性名__比较运算符=值)
                    parent_model_list = Area.objects.filter(parent__isnull=True)
                    # 将模型类转换为字典类
                    """
                    {
                        "code": "0",
                        "errmsg": "OK",
                        "province_list": [
                            {
                                "id": 110000,
                                "name": "北京市"
                            },
                            ......
                        ]
                    }
                    """
                    province_list = []
                    for parent_model in parent_model_list:
                        province_dic = {
                            "id": parent_model.id,
                            "name": parent_model.name
                        }
                        province_list.append(province_dic)

                    # 存储省份缓存数据
                    cache.set('province_list', province_list, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})

            # 响应省份数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 查询的是市区数据

            # 获取并判断是否有缓存
            sub_data = cache.get('sub_data' + area_id)
            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    # 一对应的模型类对象.多对应的模型类名小写_set 例：
                    # sub_model_list = parent_model_set.all()
                    sub_model_list = parent_model.subs.all()
                    # 将模型类转换为字典类
                    """
                    {
                        "code": "0",
                        "errmsg": "OK",
                        "sub_data": {
                            "id": 130000,
                            "name": "河北省",
                            "subs": [
                                {
                                    "id": 130100,
                                    "name": "石家庄市"
                                },
                                ......
                            ]
                        }
                    }
                    """
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dic = {
                            "id": sub_model.id,
                            "name": sub_model.name
                        }
                        subs.append(sub_dic)

                    sub_data = {
                        "id": parent_model.id,
                        "name": parent_model.name,
                        "subs": subs
                    }

                    # 存储市区缓存数据
                    cache.set('sub_data' + area_id, sub_data, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询市区数据错误'})

            # 响应市区数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
