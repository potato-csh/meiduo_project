from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import get_tracker_conf, Fdfs_client


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    # def __init__(self, option=None, client_conf=None, base_url=None):
    #     """文件存储类的初始化方法"""
    #     if client_conf is None:
    #         client_conf = get_tracker_conf(r'C:\Users\Potato\PycharmProjects\Working\meiduo_project\meiduo_mall\meiduo_mall\utils\fastdfs\client.conf')
    #
    #         print(client_conf)
    #     self.client_conf = client_conf
    #
    #     if base_url is None:
    #         base_url = settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用：文档告诉我必须重写
        :param name: 文件路径
        :param mode: 文件打开方式
        :return:None
        """
        # 因为当前不是为了打开某个文件，所以该方法无效，但是又必须重写，所以pass
        pass

    def _save(self, name, content):
        """
        保存文件会被调用：文档告诉我必须重写
        :param name: 文件路径
        :param content: 文件的二进制内容
        :return: None
        """
        # 因为当前不是为了保存某个文件，所以该方法无效，但是又需要重写，所以pass
        # client = Fdfs_client(self.client_conf)
        # res = client.append_by_buffer(content.read())
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        :return:
        文件的全路径（http://172.31.163.95:8888/group1/M00/00/00/CtM3BVnifxeAPTodAAPWWMjR7sE487.jpg）
        """
        # return 'http://172.31.163.95:8888/' + name
        return 'http://image.meiduo.site:8888/' + name
        # return settings.FDFS_BASE_UR + name

FastDFSStorage()