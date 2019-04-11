from django.contrib.auth.backends import ModelBackend
import re

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功返回数据"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """根据传入的账号获取用户信息"""
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    return user


class UsernameMobileAuthBackend(ModelBackend):
    """修改用户登录系统的后端, 支持多账户登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据传入的username获取user对象, username可以是手机号,也可以是用户名
        user = get_user_by_account(username)
        # 校检user是否存在并校检password是否正确
        if user and user.check_password(password):
            return user
