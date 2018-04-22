import re
from time import sleep

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from apps.users.models import User
from celery_tasks.tasks import send_active_mail
from dailyfresh import settings


def register(request):
    """进入注册界面 """
    return render(request, 'register.html')


def do_register(request):
    """实现注册功能 """
    # 响应请求
    return HttpResponse('注册成功，进入登录界面')


class RegisterView(View):
    """注册视图"""

    def get(self, request):
        """进入注册界面 """
        return render(request, 'register.html')

    def post(self, request):
        """实现注册功能 """

        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 用户协议， 勾选后得到：on

        # todo: 校验参数合法性
        # 判断参数不能为空
        if not all([username, password, password2, email]):
            # return redirect('/users/register')
            return render(request, 'register.html', {'errmsg': '参数不能为空'})

        # 判断两次输入的密码一致
        if password != password2:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致'})

        # 判断邮箱合法
        if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        # 判断是否勾选用户协议(勾选后得到：on)
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选用户协议'})

        # 处理业务： 保存用户到数据库表中
        # django提供的方法，会对密码进行加密
        user = None
        try:
            user = User.objects.create_user(username, email, password)  # type: User
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:
            # 判断用户是否存在
            return render(request, 'register.html', {'errmsg': '用户已存在'})

        # todo: 发送激活邮件
        token = user.generate_active_token()
        # 方式1：同步发送：会阻塞
        # RegisterView.send_active_mail(username, email, token)
        # sleep(5)
        # 方式2：使用celery异步发送：不会阻塞
        # 会保存方法名参数等到Redis数据库中
        send_active_mail.delay(username, email, token)

        # 响应请求
        return HttpResponse('注册成功，进入登录界面')

    @staticmethod
    def send_active_mail(username, email, token):
        """发送激活邮件"""
        subject = '天天生鲜激活邮件'         # 标题，必须指定
        message = ''                       # 正文
        from_email = settings.EMAIL_FROM   # 发件人
        recipient_list = [email]           # 收件人
        # 正文 （带有html样式）
        html_message = ('<h3>尊敬的%s：感谢注册天天生鲜</h3>' 
                        '请点击以下链接激活您的帐号:<br/>'
                        '<a href="http://127.0.0.1:8000/users/active/%s">'
                        'http://127.0.0.1:8000/users/active/%s</a>'
                        ) % (username, token, token)

        send_mail(subject, message, from_email, recipient_list,
                  html_message=html_message)


class ActiveView(View):

    def get(self, request, token: str):
        """
        用户激活
        :param request:
        :param token: 对字典 {'confirm':用户id} 进行加密后得到的字符串
        :return:
        """
        try:
            # 解密token
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
            # 字符串 -> bytes
            # dict_data = s.loads(token.encode())
            dict_data = s.loads(token)
        except SignatureExpired:
            # 判断是否失效
            return HttpResponse('激活链接已经失效')

        # 获取用户id
        user_id = dict_data.get('confirm')
        # 修改字段为已激活
        User.objects.filter(id=user_id).update(is_active=True)
        # 响应请求
        return HttpResponse('激活成功，跳转到登录界面')


class LoginView(View):

    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):

        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 校验合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户名和密码不能为空'})

        # 业务处理：登录(判断用户名和密码是否正确)
        user = authenticate(username=username, password=password)

        if user is None:
            # 判断用户名和密码不正确
            return render(request, 'login.html', {'errmsg': '用户名和密码不正确'})

        if not user.is_active:
            # 判断用户是否激活
            return render(request, 'login.html', {'errmsg': '用户名未激活'})

        # 登录成功，使用session保存用户登录状态
        # request.session['_auth_user_id'] = user.id
        # 使用django的login方法保存用户登录状态
        login(request, user)

        if remember == 'on':
            # 保持登录状态两周 (None会保存两周)
            request.session.set_expiry(None)
        else:
            # 关闭浏览器后，登录状态失效
            request.session.set_expiry(0)

        # 响应请求
        # return redirect('/index')
        # 注意： urls.py文件中，urlspatterns是一个列表，不要使用{}
        return redirect(reverse('goods:index'))


class LogoutView(View):

    def get(self, request):
        """注销"""
        # 调用 django的logout方法，实现退出，会删除登录用户的id（session键值对数据）
        logout(request)
        return redirect(reverse('goods:index'))


class UserInfoView(View):

    def get(self, request):
        context = {
            'which_page': 1,
        }
        return render(request, 'user_center_info.html', context)


class UserOrderView(View):

    def get(self, request):
        context = {
            'which_page': 2,
        }
        return render(request, 'user_center_order.html', context)


class UserAddressView(View):

    def get(self, request):
        context = {
            'which_page': 3,
        }
        return render(request, 'user_center_site.html', context)























