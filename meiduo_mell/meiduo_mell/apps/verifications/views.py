from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
import logging

from meiduo_mell.libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')
# Create your views here.


class SMSCodeView(APIView):
    
    def get(self, request, mobile):
        # 1. 生成验证码
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)
        # 2. 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 3. 将验证码保存到redis数据库
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 4. 发送容联云通信发送短信验证码
        # CCP().send_template_sms(手机号, [验证码, 时间], 模板)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 5. 响应
        return Response({'message': 'ok'})
    
        
        

