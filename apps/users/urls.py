from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from apps.users import views

urlpatterns = [

    # 视图函数
    # url(r'^register$', views.register, name='register'),
    # url(r'^do_register$', views.do_register, name='do_register'),

    # 类视图: as_view() 返回一个视图函数，　注意：要添加括号
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    # http://127.0.0.1:8000/users/active/JhbGciOi..mV4cCI6MTU
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'),

    url(r'^orders$', views.UserOrderView.as_view(), name='orders'),
    url(r'^address$', views.UserAddressView.as_view(), name='address'),
    url(r'^$', views.UserInfoView.as_view(), name='info'),

    # url(r'^address$', login_required(views.UserAddressView.as_view()),
    #     name='address'),
    # url(r'^address$', login_required(views.address), name='address'),

]
