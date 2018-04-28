from django.conf.urls import url, include

from apps.cart import views

urlpatterns = [

    url(r'^add$', views.AddCartView.as_view(), name='add'),

]
