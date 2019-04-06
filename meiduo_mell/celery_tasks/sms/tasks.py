from .yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import app


@app.task(name='sms_send_code')
def sms_send_code(mobile, sms_code):
    """
    发送短信的relery异步任务
    :param mobile: 手机号
    :param sms_code: 验证码
    """
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)


