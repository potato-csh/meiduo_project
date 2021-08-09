from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    """自定义模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='账号')

    # 自定义表名
    class Meta:
        db_table = 'tb_users' # 自定义表名
        verbose_name = '用户' # 单数
        verbose_name_plural = verbose_name # 复数

    def __str__(self):
        return self.username