from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis

from apps.goods.models import GoodsSKU


class AddCartView(View):
    """添加到购物车"""

    def post(self, request):

        # 判断用户是否登陆
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

        # 接收数据：sku_id， count
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 校验参数all()
        if not all([sku_id, count]):
            return JsonResponse({'code': 2, 'errmsg': '参数不完整'})

        # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '商品不存在'})

        # 判断count是否是整数
        try:
            count = int(count)
        except:
            return JsonResponse({'code': 3, 'errmsg': 'count需为整数'})

        # cart_1 = {1: 2, 2: 2}
        strict_redis = get_redis_connection('default')  # type: StrictRedis
        # 判断库存
        key = 'cart_%s' % request.user.id
        # None
        val = strict_redis.hget(key, sku_id)  # bytes
        if val:
            count += int(val)

        if sku.stock < count:
            return JsonResponse({'code': 4, 'errmsg': '库存不足'})

        # 操作redis数据库存储商品到购物车
        strict_redis.hset(key, sku_id, count)

        # 查询购物车中商品的总数量
        total_count = 0   # 购物车商品总数量
        vals = strict_redis.hvals(key)  # 列表 bytes
        for val in vals:
            total_count += int(val)    # bytes -> int

        # json方式响应添加购物车结果
        return JsonResponse({'code': 0, 'total_count': total_count})
