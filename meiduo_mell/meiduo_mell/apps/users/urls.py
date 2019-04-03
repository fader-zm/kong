from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册
    url(r'^user/$', views.User.as_view(), name='user')  # name: 路由别名, 常用于反向解析
]

