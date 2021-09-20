# meiduo_project

### 所需要的第三方包
    Django
    pymsql
    jinja2
    django_redis
    itsdangerous
    celery
    PIL：pip install Pillow
    QQLoginTool
    cryptography

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
    python manage.py makemigrations
    python manage.py migrate

### 将数据导入数据库
    mysql -h127.0.0.1 -uroot -pmysql meiduo_mall < 文件路径/goods_data.sql

### 安装redis数据库

### 安装docker以及fastdfs，并修改host的ip