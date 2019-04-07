from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


# /oauth/qq/authorization/
class QQAuthURLView(APIView):
    """拼接好QQ登录网址"""
    def get(self, request):
        # 记录是从那个页面进入到登录界面
        # next表示从哪个页面进入到登录页面, 将来登录成功后, 还返回到那个页面
        next = request.query_params.get('next') or '/'
        
        # 利用QQ登录SDK
        # 创建QQ登录工具对象
        QQ_CLIENT_ID = '101514053'
        QQ_CLIENT_SECRET = '1075e75648566262ea35afa688073012'
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
        # OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri='回调域名', state='记录来源')
        oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI, state=next)
        # 拼接QQ登录url
        login_url = oauth.get_qq_url()
        # 响应
        return Response({'login_url': login_url})



