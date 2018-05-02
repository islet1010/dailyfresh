from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis

from apps.goods.models import GoodsSKU
from apps.users.models import Address
from utils.common import LoginRequiredMixin


class PlaceOrderView(LoginRequiredMixin, View):

    def post(self, request):

        # 获取请求参数：sku_ids，count
        count = request.POST.get('count')
        sku_ids = request.POST.getlist('sku_ids')  # 一键多值

        # 校验参数合法性
        if not sku_ids:
            # 如果商品id为空，跳转到购物车界面
            return redirect(reverse('cart:info'))

        # todo: 查询业务数据： 地址，购物车商品，总数量，总金额
        # 获取用户地址信息
        try:
            # Address.objects.filter(user=request.user).order_by('-create_time')[0]
            address = Address.objects.filter(user=request.user).latest('create_time')
        except:
            # 查询不到地址信息，则用户需要点击页面中的按钮，新增地址
            address = None

        skus = []           # 要显示的商品列表
        total_count = 0     # 商品总数量
        total_amount = 0    # 商品总金额

        strict_redis = get_redis_connection() # type: StrictRedis
        # cart_1 = {1: 2, 2: 2}
        key = 'cart_%s' % request.user.id

        # 如果是从购物车页面过来，商品的数量从redis中获取
        if count is None:
            # 循环商品id： sku_ids
            for sku_id in sku_ids:
                # 查询商品对象
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except GoodsSKU.DoesNotExist:
                    # 如果商品id为空，跳转到购物车界面
                    return redirect(reverse('cart:info'))

                # 获取商品数量和小计金额(类型转换)
                count = strict_redis.hget(key, sku_id)  # bytes
                count = int(count)
                amount = sku.price * count

                # 动态地给商品对象新增实例属性(count, amount)
                sku.count = count
                sku.amount = amount

                # 添加商品对象到列表中
                skus.append(sku)

                # 累计商品总数量和总金额
                total_count += sku.count
                total_amount += sku.amount
        else:
            # 如果是从详情页面过来，商品的数量从request中获取（只有一个商品）
            sku_id = request.POST.get('sku_ids')

            # 查询商品对象
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                # 如果商品id为空，跳转到购物车界面
                return redirect(reverse('cart:info'))

            # 获取商品数量和小计金额(类型转换)
            count = int(count)
            amount = sku.price * count

            # 判断库存：详情页没有判断库存
            if count > sku.stock:
                # 库存不足，跳转回详情界面
                return redirect(reverse('goods:detail', args=[sku_id]))

            # 动态地给商品对象新增实例属性(count, amount)
            sku.count = count
            sku.amount = amount

            # 添加商品对象到列表中
            skus.append(sku)

            # 累计商品总数量和总金额
            total_count += sku.count
            total_amount += sku.amount

            # 将商品数量保存到`Redis`中（以便取消操作在购物车中还能看得到商品）
            # cart_1 = {1: 2, 2: 2}
            strict_redis.hset(key, sku_id, count)

        # 运费(固定)
        trans_cost = 10
        # 实付金额
        total_pay = total_amount + trans_cost

        # 定义模板显示的字典数据
        context = {
            'skus': skus,
            'address': address,
            'total_count': total_count,
            'total_amount': total_amount,
            'trans_cost': trans_cost,
            'total_pay': total_pay,
        }

        # 响应结果: 返回确认订单html界面
        return render(request, 'place_order.html', context)

