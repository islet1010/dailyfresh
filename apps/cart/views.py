from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis

from apps.goods.models import GoodsSKU
from utils.common import LoginRequiredMixin


class CartDeleteView(View):

    # /cart/delete
    def post(self, request):
        """删除购物车中的商品"""

        # 判断用户是否有登录
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

        # 获取用户提交的参数
        sku_id = request.POST.get('sku_id')

        # 参数不能为空
        if not sku_id:
            return JsonResponse({'code': 2, 'errmsg': '商品id不能为空'})

        # todo: 业务处理: 删除redis中对应的商品
        # cart_1: {'1': '2', '2': '2'}
        strict_redis = get_redis_connection()  # type: StrictRedis
        key = 'cart_%s' % request.user.id
        # 删除hash中的一个字段和值: hdel
        strict_redis.hdel(key, sku_id)

        # todo: 查询购物车中商品的总数量
        total_count = 0   # 购物车商品总数量
        vals = strict_redis.hvals(key)  # 列表 bytes
        for val in vals:
            total_count += int(val)    # bytes -> int

        # json方式响应添加购物车结果
        return JsonResponse({'code': 0, 'total_count': total_count})


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


class CartInfoView(LoginRequiredMixin, View):

    def get(self, request):
        """显示购物车界面"""
        # 获取登录用户id
        user_id = request.user.id

        # 定义一个列表，保存用户购物车中所有的商品
        skus = []
        # 总数量
        total_count = 0
        # 总金额
        total_amount = 0

        # 从Redis中查询出当前登录用户的商品
        # cart_1 = {1: 2 , 2: 2}
        strict_redis = get_redis_connection()  # type: StrictRedis
        key = 'cart_%s' % user_id
        # 获取所有的键（商品id）  列表（bytes）
        sku_ids = strict_redis.hkeys(key)
        for sku_id in sku_ids:
            # 从mysql中查询出对应的商品对象
            sku = GoodsSKU.objects.get(id=int(sku_id))  # bytes -> int
            # 获取商品数量
            count = strict_redis.hget(key, sku_id)  # bytes
            # 计算商品的小计金额
            amount = sku.price * int(count)

            # todo: 给商品对象新增实例属性： 数量 小计金额amount
            sku.count = int(count)
            sku.amount = amount

            # todo: 累计总数量和总金额
            total_count += int(count)
            total_amount += amount

            skus.append(sku)

        # 定义模板数据
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
        }

        # 响应请求，显示html界面
        return render(request, 'cart.html', context)


class CartUpdateView(View):

    def post(self, request):
        """修改商品数量"""

        if not request.user.is_authenticated():
            return JsonResponse({'code':1, 'errmsg': '请先登录'})

        # 获取参数：sku_id, count
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 校验参数all()
        if not all([sku_id, count]):
            return JsonResponse({'code':2, 'errmsg': '参数不能为空'})

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

        # 判断库存
        if count > sku.stock:
            return JsonResponse({'code': 4, 'errmsg': '库存不足'})

        # 如果用户登陆，将修改的购物车数据存储到redis中
        strict_redis = get_redis_connection()   # type : StrictRedis
        key = 'cart_%s' % request.user.id
        strict_redis.hset(key, sku_id, count)

        # 查询购物车中商品的总数量
        total_count = 0   # 购物车商品总数量
        vals = strict_redis.hvals(key)  # 列表 bytes
        for val in vals:
            total_count += int(val)    # bytes -> int

        # json方式响应添加购物车结果
        return JsonResponse({'code': 0, 'total_count': total_count})















