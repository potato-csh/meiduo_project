import time, os
from collections import OrderedDict
from django.template import loader
from django.conf import settings

from contents.utils import get_categories
from contents.models import ContentCategory, Content




def generate_static_index_html():
    """静态化首页"""
    print('%s: generate_static_index_html' % time.ctime())

    # 查询商品分类和频道
    categories = get_categories()

    # 查询首页广告数据
    # 查询所有的广告类别
    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        # 使用广告类别查询出该类别对应的所有的广告内容
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by(
            'sequence')  # 查询出未下架的广告并排序

    # 渲染模板的上下文
    context = {
        'categories': categories,
        'contents': contents,
    }

    # 获取首页模板文件
    template = loader.get_template('index.html')
    # 渲染首页模板文件
    html_text = template.render(context)
    # 将首页html字符串写到制定目录,命名为'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
