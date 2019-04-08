from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from . import constants
from .models import OauthQQUser
from .utils import generate_save_user_token
from .serializers import QQAuthUserSerializers

# Create your views here.
logger = logging.getLogger('django')


# /oauth/qq/authorization/
class QQAuthURLView(APIView):
    """拼接好QQ登录网址"""
    def get(self, request):
        # 记录是从那个页面进入到登录界面
        # next表示从哪个页面进入到登录页面, 将来登录成功后, 还返回到那个页面
        next = request.query_params.get('next') or '/'
        
        # 利用QQ登录SDK
        # 创建QQ登录工具对象
        # OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri='回调域名', state='记录来源')
        oauth = OAuthQQ(client_id=constants.QQ_CLIENT_ID, client_secret=constants.QQ_CLIENT_SECRET,
                        redirect_uri=constants.QQ_REDIRECT_URI, state=next)
        # 拼接QQ登录url
        login_url = oauth.get_qq_url()
        # 响应
        return Response({'login_url': login_url})


class QQAuthUserView(APIView):
    """用户扫码登录的回调处理"""
    def get(self, request):
        # 1. 提取code请求参数
        code = request.query_params.get('code') or None
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        # 2. 创建QQ登录工具对象, 传入code获取access_token值
        oauth = OAuthQQ(client_id=constants.QQ_CLIENT_ID, client_secret=constants.QQ_CLIENT_SECRET,
                        redirect_uri=constants.QQ_REDIRECT_URI, state=next)
        try:
            access_token = oauth.get_access_token(code)
            # 3. 传入access_token值, 获取open_id
            open_id = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response({'message': 'QQ服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 4. 使用openid查询该QQ用户是否绑定过商城中的用户
        try:
            oauth_qquser = OauthQQUser.objects.get(openid=open_id)
        except OauthQQUser.DoesNotExist:
            # 5. 如果openid没有绑定过, 则创建用户并绑定openid
            # 6.如果openid 没有绑定用户,把openid 加密之后响应给前端 ,让前端先暂存一会 等待绑定时使用
            access_token_openid = generate_save_user_token(open_id)
            return Response({
                "access_token": access_token_openid
            })
        else:
            # 获取oauth_qquser关联的user
            user = oauth_qquser.user
            
            # 6. 如果openid绑定过用户, 则生成JWT token, 并返回
            # 生成记录登录状态的token
            from rest_framework_jwt.settings import api_settings
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用 生成jwt
            payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
            token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
            
            return Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
        
    def post(self, request):
        """使用openid 绑定用户"""
        # 获取序列化对象
        serializer = QQAuthUserSerializers(data=request.data)
        # 开启校验
        serializer.is_valid(raise_exception=True)
        # 保存校验结果, 并获取user对象
        user = serializer.save()
        
        # 生成 JWT token, 并响应
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        
        return Response({
            'token': token,
            'userid': user.id,
            'username': user.username
        })


# class UserDetailView():
        
        

