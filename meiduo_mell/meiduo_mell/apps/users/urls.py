from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册
    url(r'^users/$', views.UserView.as_view(), name='user'),  # name: 路由别名, 常用于反向解析
    
    # 判断用户名是否已注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
]

