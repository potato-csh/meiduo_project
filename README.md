pip# meiduo_project
    参考：https://github.com/pywjh/MeiDuoByDjango1

### 每次需要修改
    host里面的ip
    utils/fastdfs/client.conf里面的ip
    settings/dev里面的Haystack
    配置文件中HAYSTACK_CONNECTIONS的ip，并进入/home/python/elasticsearc-2.4.6/config/elasticsearch.yml第的ip

### 所需要的第三方包
    Django
    pymysql
    jinja2
    django_redis
    itsdangerous
    celery
    PIL：pip install Pillow
    QQLoginTool
    cryptography
    django-haystack
    elasticsearch==2.4.1
    django_crontab
    python-alipay-sdk --upgrade
    
    $ pip install fdfs_client-py-master.zip
    $ pip install mutagen
    $ pip install requests

### 新建数据库用户
    1.新建MySQL数据库：meiduo_mall
        create database meiduo charset=utf8;

    2.新建MySQL用户**
        create user itheima identified by '123456';

    3.授权`itcast`用户访问`meiduo_mall`数据库
        grant all on meiduo.* to 'itheima'@'%';

    4.授权结束后刷新特权
        flush privileges;

#### 迁移数据库对象
    ython manage.py makemigrations
    python manage.py migrate

### 将数据导入数据库
    mysql -h127.0.0.1 -uroot -pmysql meiduo_mall < 文件路径/goods_data.sql

### 安装redis数据库

### 安装docker以及fastdfs，并修改host的ip

### host文件
    127.0.0.1	www.meiduo.site
    192.168.100.28		image.meiduo.site

### 沙盒账户
    商家账号idjher8847@sandbox.com
    商户UID2088621956628582
    登录密码111111

    买家信息
    买家账号vbedeb9122@sandbox.com
    登录密码111111
    支付密码111111


