from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin

from .serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, AddressSerializer, \
    AddressTitleSerializer
from .models import User, Address
import rest_framework.request


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


# 更新邮箱 视图类
class EmailView(UpdateAPIView):
    """更新邮箱"""
    # 1. 用户权限认证, 验证用户是否登录
    permission_classes = [IsAuthenticated]
    # 2. 指定序列化器
    serializer_class = EmailSerializer
    
    # 3. 重写get_object方法, 获取模型对象
    def get_object(self):
        return self.request.user


# 邮箱验证
class VerifyEmailView(APIView):
    """激活用户邮箱"""
    
    def get(self, request):
        # 1. 获取token参数
        token = request.query_params.get('token')
        # 2. 验证token, 提取user
        if not token:
            return Response({'message': 'token缺失'}, status=status.HTTP_400_BAD_REQUEST)
        # 将token解密, 并获取查询对象的user
        user = User.check_verify_email_token(token)
        # 3. email_active改为True
        if not user:
            return Response({'message': '邮箱激活失败'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        # 4. 响应
        return Response({'message': 'ok'})
    
    
class AddressViewSet(UpdateModelMixin, GenericViewSet):
    """收货地址的增删改查 crud"""
    
    # 登录用户认证
    permission_classes = [IsAuthenticated]
    
    # 指定查询集
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)
    
    # 指定序列化器
    serializer_class = AddressSerializer
    
    def create(self, request):
        """新增收货地址"""
        """因为新增收货地址有上限, 因此要重新create方法"""
        # count = request.user.addresses.all().count()  # 利用一查多
        count = Address.objects.filter(user=request.user).count()  # 关联过滤查询, 以外键为条件
        if count >= 20:
            return Response({'message': '新增收货地址已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建序列化器进行反序列化
        serializer = self.get_serializer(data=request.data)
        # 调用序列化器is_valied()
        serializer.is_valid(raise_exception=True)
        # 调用序列化器save()
        serializer.save()
        # 响应
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """用户收货地址列表数据"""
        # 获取查询集
        queryset = self.get_queryset()
        # 创建序列化器ser
        serializer = self.get_serializer(queryset, many=True)
        
        user = request.user
        return Response({
            'user_id': user.id,
            'default_addresses_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除收货地址"""
        # 获取要删除的收货地址模型对象
        address = self.get_object()
        # 删除该收货地址
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # # 表示路径名格式应该为 addresses/{pk}/title/
    # @action(methods=['put'], detail=True)
    # def title(self, request, *args, **kwargs):
    #     """修改地址标题"""
    #     # 获取要修改的地址模型对象
    #     addresses = self.get_object()
    #     # 获取要更改标题
    #     title = request.data.get('title')
    #     addresses.title = title
    #     addresses.save()
    #     return Response({'title': title})

    # 表示路径名格式应该为 addresses/{pk}/title/
    @action(methods=['put'], detail=True)
    def title(self, request, *args, **kwargs):
        """修改地址标题"""
        # 获取要修改的地址模型对象
        addresses = self.get_object()
        # 创建序列化器进行反序列化
        serializer = AddressTitleSerializer(instance=addresses, data=request.data)
        # 调用序列化器的is_valid()
        serializer.is_valid()
        # 调用序列化器的save()
        serializer.save()
        # 响应
        return Response(serializer.data)
    
    # addresses/{pk}/status   addresses/1/status/
    @action(methods=['put'], detail=True)
    def status(self, request, *args, **kwargs):
        """设置默认收货地址"""
        # 获取user, 哪个用户
        user = request.user
        # 获取收货地址模型对象
        address = self.get_object()
        user.default_address = address
        user.save()
        return Response({'message': 'OK'})
