import re
from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from users.models import User
from meiduo_mall.utils.response_code import RETCODE


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
            提供注册界面
            :param request: 请求对象
            :return: 注册界面
        """
        return render(request, 'register.html')

    def post(self, request):
        # 1、接收请求提取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 2、检验参数
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5~20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match('^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8~20个字符的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次密码不一致')
        # 判断手机号是否合法
        if not re.match('^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # 3、保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 4、状态保持
        login(request, user)

        # 5、响应注册结果
        # return http.HttpResponse('注册成功，重定向到首页')
        return redirect(reverse('contents:index'))


class UsernameCountView(View):
    """判断用户是否重复注册"""

    def get(self, request, username):
        """
        :param request:
        :param username:
        :return:
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复"""

    def get(self, request, mobile):
        """

        :param request:
        :param mobile:
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
