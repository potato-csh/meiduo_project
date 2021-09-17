from django import http
from django.shortcuts import render
from django.views import View
# 分页器（有100万文字，需要制作成为一本书，先规定每页多少文字，然后得出一共多少页）
# 数据库中的记录就是文字，我们需要考虑在分页时每页记录的条数，然后得出一共多少页
from django.core.paginator import Paginator

from goods.models import GoodsCategory, SKU
from contents.utils import get_categories
from goods.utils import get_breadcrumb


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
        page_skus = paginator.page(page_num)
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
