from django.core.files.storage import Storage
from django.conf import settings


class MyStorage(Storage):
    """自定义文件存储类"""

    def __init__(self, option=None):
        """文件存储类的初始化方法"""
        if not option:
            option = settings.CUSTOM_STORAGE_OPTIONS

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
        pass

    def
