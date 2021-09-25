from django import http
from django.shortcuts import render
from django.views import View
# 分页器（有100万文字，需要制作成为一本书，先规定每页多少文字，然后得出一共多少页）
# 数据库中的记录就是文字，我们需要考虑在分页时每页记录的条数，然后得出一共多少页
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone # 处理时间的工具
from datetime import datetime

from goods.models import GoodsCategory, SKU,GoodsVisitCount
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE


# Create your views here.

class ListViews(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """展示并渲染商品列表页"""
        # 检验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)  # 查询出来的categories是三级目录
        except Exception as e:
            return http.HttpResponseForbidden('参数category_id错误')

        # 获取sort（排序规则）：如果sort没有值，则取 'default'
        # sort = request.GET.get('键',默认值)
        sort = request.GET.get('sort', 'default')
        # 根据sort选择排序字段，排序字段必须是模型类型的属性
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            # 只要不是'price'和'-sales'都属于default情况
            sort = 'default'  # 当出现？sort=itheima的情况下属于默认情况
            sort_field = 'create_time'

        # 查询商品分类
        categories = get_categories()

        # 面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 排序和分页查询
        # 查询出商品的库存量，用category查询sku；一查多：一方的模型对象.多方关联字段.all/filter()
        # skus = SKU.objects.filter(category=category, is_launched=True)  # 没经验的写法
        # skus = SKU.objects.filter(categor_id=category_id, is_launched=True)  # 没经验的写法
        # skus = category.sku_set.filter(is_launched=True).order_by(sort=排序方式：default/price/hot)  # 有经验的写法
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)  # 有经验的写法

        # 创建分页器
        # Paginator('要分页的记录', '每页记录的条数')
        paginator = Paginator(skus, 5)
        # 获取到当前页码的那一页
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return http.HttpResponseNotFound('EmptyPage')

        # 获取总页数
        total_page = paginator.num_pages  # 给前端的插件使用

        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后的数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页数
        }

        return render(request, 'list.html', context)


class HotGoodsView(View):
    """商品热销排行"""

    def get(self, request, category_id):
        # 查询指定分类的SKU信息，而且必须是上架的状态，然后按照销量由高到低排序，最后切片取出前两位
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 将模型列表转字典列表，构造JSON数据
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url  # 记得要取出全路径
            }
            hot_skus.append(sku_dict)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取并校验数据
        try:
            # 获取当前sku的信息
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            # return http.HttpResponseNotFound('sku_id 不存在')
            return render(request, '404.html')

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self,request,category_id):
        """记录分类商品访问量的逻辑业务"""
        # 获取并校验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')

        date = timezone.now()   # 获取当前的时期时间对象

        # 判断当天中指定分类商品对应的记录是否存在
        try:
            # 若存在，直接获取到对应的对象
            # counts_data = GoodsVisitCount.objects.get(data='当天日期',category=category)
            counts_data = GoodsVisitCount.objects.get(category=category,date=date)
        except GoodsVisitCount.DoesNotExist:
            # 若不存在，则直接创建对应的对象
            counts_data = GoodsVisitCount(
                category = category
            )

        # 无论是新创建的记录还是之前已存在都要为count 累加
        counts_data.count += 1
        counts_data.save()

        # 返回响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})