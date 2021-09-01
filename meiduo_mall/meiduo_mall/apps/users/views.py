import re, json, logging
from django import http
from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
from itsdangerous import BadData

from users.models import User, Address
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.email.tasks import send_verify_email
from .utils import generate_verify_email_url, check_verify_email_token
from .constants import *

# 创建日志生成器
logger = logging.getLogger('django')


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """
        提供登录界面
        :param request: 请求对象
        :return: 登录界面
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """

        # 1、接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2、校验参数

        # 判断参数是否齐全
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        # 3、认证登录用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或者密码错误'})

        # 4、状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住登录：状态保持在浏览器会话结束后就销毁
            request.session.set_expiry(0)
        else:
            # 记住用户：none代表两周后过期
            request.session.set_expiry(None)

        # 5、响应结果
        # 先取出next
        next = request.GET.get('next')
        if next:
            # 重定向到next
            response = redirect(next)
        else:
            # 重定向到首页
            response = redirect(reverse('contents:index'))

        # 为了实现在首页的右上角展示用户名信息，我们需要将用户名缓存到cookie中
        # response.set_cookie('key', 'val', 'expiry')
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


# LoginRequiredMixin中自带is_authenticated，要求LoginRequiredMixin必须作为第一个参数
class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))

        # 如果LoginRequiredMixin判断出用户已登录，那么request.user就是登录用户对象
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """查询并展示收货地址界面"""

        # 获取当前登录用户
        login_user = request.user

        # 使用当前登录用户和is_deleted=False作为条件查询地址数据
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        # 将用户地址模型列表转字典列表:因为JsonResponse和Vue.js不认识模型类型，只有Django和Jinja2模板引擎认识
        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email,
            }
            address_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'address': address_list
        }

        return render(request, 'user_center_site.html', context=context)


class AddressCreateView(LoginRequiredMixin, View):
    """新增地址"""

    def post(self, request):
        """新增地址的逻辑"""

        # 判断用户地址数量是否超过上限：查询当前登录用户的地址数量
        # count = Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()  # 一查多，使用related_name查询
        if count > USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '用户地址数量已超过上限'})

        # 获取参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            # 将数据保存到mysql数据库
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 如果登录用户没有默认的地址，我们需要指定默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 创建新增结果字典
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,

        }

        # 响应新增地址结果，将结果响应给前端页面进行渲染
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """更新和删除收货地址"""

    def put(self, request, address_id):
        """更新收货地址的逻辑"""

        # 获取参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            # 使用最新的地址信息覆盖指定的旧的地址信息
            # address = Address.objects.get('address_id')
            # address.user = ''
            # 这个结果是响应的行数，并不是模型类
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改收货地址失败'})

        # 响应新的地址信息给前端渲染
        address = Address.objects.get(id=address_id)
        addres_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改收货地址成功', 'address': addres_dict})

    def delete(self, request, address_id):
        """删除收货地址的逻辑"""

        try:
            # 实现指定地址的逻辑删除：is_delete=True
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除收货地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除收货地址成功'})


class DefaultAddressView(LoginRequiredMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址的逻辑"""
        try:
            # 查询出当前哪个地址会作为登录用户的默认地址
            address = Address.objects.get(id=address_id)

            # 将指定的地址设置为当前登录用户的默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '已设置为默认地址'})


class EmailView(LoginRequiredMixin, View):
    """添加邮箱"""

    def put(self, request):
        """实现添加邮箱业务逻辑"""
        # 获取参数
        json_str = request.body.decode()  # body是byte类型
        json_dic = json.loads(json_str)
        email = json_dic.get('email')

        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 将输入的email传入到用户数据库中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 发送邮件验证邮箱
        verify_url = generate_verify_email_url(request.user)
        # send_verify_email(email, verify_url) # 错误的写法
        send_verify_email.delay(email, verify_url)  # 一定要记得调用delay

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        # 接收参数
        token = request.GET.get('token')

        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token')

        # 从token中提取用户信息user_id ==> user
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')

        # 将用户的email_active字段设置为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        # 响应结果：重定向到用户中心
        return redirect(reverse('users:info'))


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """
        实现退出登录逻辑
        :param request:
        :return:
        """
        # 清理session
        logout(request)
        # 退出登录，重定向到首页
        response = redirect(reverse('contents:index'))
        # 退出登录清除cookie中的username
        response.delete_cookie('username')

        return response


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
        sms_code_client = request.POST.get('sms_code')
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

        # 判断短信验证码输入是否正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'errmsg': '输入短信验证码有误'})

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
        response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


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
