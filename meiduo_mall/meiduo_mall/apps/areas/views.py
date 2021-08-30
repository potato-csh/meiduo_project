from django.shortcuts import render
from django.views import View


# Create your views here.


class AreaView(View):
    """省市区三级联动"""

    def get(self, request):
        # 判断当前是要查询省份数据还是市区数据
        area_id = request.GET.get('area_id')

        if not area_id:
            # 查询的为省份数据
            pass