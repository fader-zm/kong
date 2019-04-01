from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
import logging
from rest_framework import status

from celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
from celery_tasks.sms import tasks

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
        
        # 创建redis管道: (把多次redis操作装入管道中, 将来一次性去执行, 减少redis连接操作)
        pl = redis_conn.pipeline()
        # # 5. 将验证码保存到redis数据库
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # # 6. 存储一个标记, 表示此手机号已发送短信验证码 标记
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道
        pl.execute()
        
        # 7. 发送容联云通信发送短信验证码
        # CCP().send_template_sms(手机号, [验证码, 时间], 模板)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//6], 1)
        tasks.sms_send_code.delay(mobile, sms_code)
        # 8. 响应
        return Response({'message': 'ok'})
    
        
        

