from django.contrib import admin

from apps.goods.models import *

admin.site.register(GoodsCategory)
admin.site.register(GoodsSPU)
admin.site.register(GoodsSKU)
admin.site.register(IndexSlideGoods)
admin.site.register(IndexPromotion)
admin.site.register(IndexCategoryGoods)
