from django.conf.urls import url, include

from apps.goods import views

urlpatterns = [

    url('^index$', views.IndexView.as_view(), name='index'),
    # http://127.0.0.1:8000/detail/商品id
    url('^detail/(\d+)$', views.DetailView.as_view(), name='detail'),
    # http://127.0.0.1:8000/list/category_id/page_num?sort=default
    url('^list/(\d+)/(\d+)$', views.ListView.as_view(), name='list'),

]
