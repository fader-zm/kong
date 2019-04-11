from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import CreateUserSerializer, UserDetailSerializer
from .models import User


# 定义用户视图类
class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器类
    serializer_class = CreateUserSerializer


# 判断用户名是否已被注册
class UsernameCountView(APIView):
    """判断用户名是否已被注册"""
    
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


# 判断手机号是否已经被注册
class MobileConutViwe(APIView):
    """判断手机号是否已经被注册"""
    
    def get(self, request, mobile):
        # 查询user表
        count = User.objects.filter(mobile=mobile).count()
        # 包装响应数据
        data = {
            'mobile': mobile,
            'count': count
        }
        # 响应
        return Response(data=data)


# 定义用户中心视图类
class UserDetailViwe(RetrieveAPIView):
    """用户详细信息接口"""
    # 登录用户身份认证
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = UserDetailSerializer
    
    # 重写get_object方法获取用户详情信息
    def get_object(self):
        return self.request.user
    
"""
queryset.get(pk=1)
 queryset.get(**{pk:1})
 User.objects.get(id=1)
"""
