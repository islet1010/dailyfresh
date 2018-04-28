from django.conf.urls import url, include

from apps.cart import views

urlpatterns = [

    url(r'^add$', views.AddCartView.as_view(), name='add'),     # 添加商品到购物车
    # /cart
    url(r'^$', views.CartInfoView.as_view(), name='info'),      # 进入购物车界面

]
