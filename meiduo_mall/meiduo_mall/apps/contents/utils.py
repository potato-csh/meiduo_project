from collections import OrderedDict
from goods.models import GoodsChannelGroup, GoodsChannel, GoodsCategory


def get_categories():
    # 准备商品分类对应的字典
    # categories = []
    categories = OrderedDict()  # 保证有序

    # 查询所有的商品频道:37个一级类别
    channels = GoodsChannel.objects.all().order_by('group_id', 'sequence')
    for channel in channels:
        # 获取当前频道所在组
        group_id = channel.group_id  # 当前组

        # 构造基本的数据框架:只有11个组
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 查询当前频道对应的一级类别
        cat1 = channel.category
        # 将cat1添加到channels中
        categories[group_id]["channels"].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # 获取二级类别和三级类别
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]["sub_cats"].append(cat2)

    return categories
