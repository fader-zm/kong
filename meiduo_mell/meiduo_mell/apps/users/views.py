from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from .serializers import CreateUserSerializer


# 定义用户视图类
class User(CreateAPIView):
    """用户注册"""
    # 指定序列化器类
    serializer_class = CreateUserSerializer
