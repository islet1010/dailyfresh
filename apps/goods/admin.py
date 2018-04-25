from django.contrib import admin
from celery_tasks.tasks import *
from apps.goods.models import *


class BaseAdmin(admin.ModelAdmin):

    # list_display = ['id', 'name']
    def save_model(self, request, obj, form, change):
        """在管理后台新增或修改了模型数据后调用"""
        super().save_model(request, obj, form, change)
        print('save_model: %s ' % obj)
        # 通过celery异步生成静态的首页
        generate_static_index_page.delay()

    def delete_model(self, request, obj):
        """在管理后台删除一条数据时调用"""
        super().delete_model(request, obj)
        print('delete_model: %s ' % obj)
        # 通过celery异步生成静态的首页
        generate_static_index_page.delay()


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsSPUAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    list_display = ['id']
    pass


admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexSlideGoods, IndexSlideGoodsAdmin)
admin.site.register(IndexPromotion, IndexPromotionAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)
