from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from apps.users.models import User
from apps.users.views import UserAddressView


class IndexView(View):

    def get(self, request):
        print(UserAddressView.__mro__)

        # 显示登录的用户名
        # 方式1：主动查询登录用户并显示
        # user_id = request.session.get('_auth_user_id')
        # user = User.objects.get(id=user_id)
        # context = {'user': user}
        # return render(request, 'index.html', context)

        # 方式2：使用django用户认证模块，直接显示
        # django会自动查询登录的用户对象，会保存到request对象中
        # 并且会把user对象传递给模块
        # user = request.user
        return render(request, 'index.html')





