from django.conf.urls import url, include

from apps.orders import views

urlpatterns = [

    # /orders/place 确认订单界面
    url(r'^place$', views.PlaceOrderView.as_view(), name='place'),
]
