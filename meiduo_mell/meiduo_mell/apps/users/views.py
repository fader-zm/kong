from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import CreateUserSerializer
from .models import User


# 定义用户视图类
class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器类
    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    """判断用户是否已被注册"""
    
    def get(self, request, username):
        # 查询user表
        count = User.objects.filter(username=username).count()
        # 包装响应数据
        data = {
            'username': username,
            'count': count
        }
        # 响应
        return Response(data=data)
