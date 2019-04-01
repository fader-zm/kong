from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.


class SMSCodeView(APIView):
    
    def get(self, request, mobile):
        # 1. 生成验证码
        # 2. 创建redis连接对象
        # 3. 将验证码保存到redis数据库
        # 4. 发送容联云通信发送短信验证码
        # 5. 响应
        pass
        
        

