"""celery的入口"""
import os
from celery import Celery

# 为celery添加django配置文件
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建celery实例
celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery文件
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
