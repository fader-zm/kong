from django.conf.urls import url

from .views import QQAuthURLView, QQAuthUserView

urlpatterns = [
    # qq登录页面回调
    url(r'^qq/authorization/$', QQAuthURLView.as_view()),
    # 用户扫码登录的回调处理
    url(r'^qq/user/$', QQAuthUserView.as_view()),
]
