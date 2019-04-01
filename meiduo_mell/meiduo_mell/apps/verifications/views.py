from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
import logging
from rest_framework import status

from meiduo_mell.libs.yuntongxun.sms import CCP
from . import constants

logger = logging.getLogger('django')
# Create your views here.


class SMSCodeView(APIView):
    
    def get(self, request, mobile):
        # 1. 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 2. 先从获取redis的发送标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 3. 如果取到标记说明此手机号频繁发短信
        if send_flag:
            return Response({'message': '手机频繁发短信'}, status=status.HTTP_400_BAD_REQUEST)
        # 4. 生成验证码
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)
        
        # 5. 将验证码保存到redis数据库
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 6. 存储一个标记, 表示此手机号已发送短信验证码 标记
        redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 7. 发送容联云通信发送短信验证码
        # CCP().send_template_sms(手机号, [验证码, 时间], 模板)
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//6], 1)
        # 8. 响应
        return Response({'message': 'ok'})
    
        
        

