from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from .utils import check_save_user_token
from .models import OauthQQUser


class QQAuthUserSerializers(serializers.Serializer):
    """
    QQ 登录创建用户序列化
    """
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='password', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')
    
    def validate(self, attrs):
        """
        :param attrs:
        :return:
        """
        # 1. 校验access_token
        # 获取access_token
        access_token = attrs['access_token']
        # 获取身份凭证
        openid = check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError('无效的access_token')
        
        # 将openid方法校检字典中, 后面会用到
        attrs['openid'] = openid
        
        # 校验短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        # 创建redis数据库链接
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        
        if not real_sms_code:
            raise serializers.ValidationError('验证码失效')
        
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码异常')
        
        # 如果用户存在, 检查用户密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            """校检password"""
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        """
        创建新用户, 并绑定openid
        :param validated_data: data
        :return: user
        """
        # 获取校验的用户
        user = validated_data.get('user')
        # 如果用户不存在, 新建用户
        if not user:
            user = User(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile'),
            )
            user.set_password(validated_data.get('password'))
            user.save()
        # 将用户绑定 openid
        OauthQQUser.objects.create(
            openid=validated_data.get('openid'),
            user=user
        )
        # 返回用户数据 user
        return user
