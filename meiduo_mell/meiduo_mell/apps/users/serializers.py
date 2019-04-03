from rest_framework import serializers
import re
from django_redis import get_redis_connection

from .models import User

# 定义序列化器


class CreateUserSerializer(serializers.Serializer):
    """注册序列化器"""
    # 序列化器的所有字段: ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    # 需要校检的字段: ['username', 'password', 'password2', 'moblie', 'sms_code', 'allow']
    # 模型中已存在的字段: ['username', 'password', 'mobile']  # 对于模型中不存在的字段, 要自定义创建
    
    # 需要序列化的字段: ['id', 'username', 'mobile']  # 发送给前端的数据, 根据前端需求返回
    # 需要反序列化的字段: ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    
    class Meta:
        model = User  # 从User模型中映射序列化器字段
        # fields = '__all__'  # 指定要映射的字段
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
        extra_kwargs = {  # 修改字段选项
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_message': {  # 自定义校检出错后信息提示
                    'min_length': '仅允许5-20字符的用户名',
                    'max_length': '仅允许5-20字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_message': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
        
        # 传入什么就返回什么
        def validate_mobile(self, value):
            """单独校检手机号"""
            if not re.match(r'1[3-9]\d{9}$]', value):
                raise serializers.ValidationError('')
            return value
        
        def validate_allow(self, value):
            """校检是否同意协议"""
            if value != 'true':
                raise serializers.ValidationError('请同意用户协议')
            return value
        
        def validate(self, attrs):
            """校检两个密码是否相同"""
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError('密码不一致')
            
            # 校检验证码
            redis_conn = get_redis_connection('verify_codes')
            mobile = attrs['mobile']
            real_sms_code = redis_conn.get('sms_%s' % mobile)
            # 向redis数据库存储都是以字符串存储的, 取出来后都是bytes类型 [bytes]
            
            if real_sms_code or attrs['sms_code'] != real_sms_code.decode():
                raise serializers.ValidationError('验证码错误')
            
            return attrs
        
        def create(self, validated_data):
            # 把不需要存储的 password2, sms_code, allow 从字段中移出
            del validated_data['password2']
            del validated_data['sms_code']
            del validated_data['allow']
            
            # 先取出password
            password = validated_data.pop('password')
            # 创建用户模型, 给模型中的 username和mobile 赋值
            
            user = User(**validated_data)
            user.set_password(password)
            user.save()  # 存储到数据库
            return user
            


