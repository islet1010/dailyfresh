from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion
from apps.users.models import User
from apps.users.views import UserAddressView


class IndexView(View):

    def get2(self, request):
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

    def get(self, request):

        # 查询首页商品数据：商品类别，轮播图， 促销活动
        categories = GoodsCategory.objects.all()
        slide_skus = IndexSlideGoods.objects.all().order_by('index')
        promotions = IndexPromotion.objects.all().order_by('index')[0:2]

        # 定义模板显示的数据
        context = {
            'categories': categories,
            'slide_skus': slide_skus,
            'promotions': promotions,
        }

        # 响应请求
        return render(request, 'index.html', context)





