from rest_framework import serializers
import re
from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_verify_email
from .models import User, Address

# 定义序列化器


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    # 序列化器的所有字段: ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    # 需要校检的字段: ['username', 'password', 'password2', 'moblie', 'sms_code', 'allow']
    # 模型中已存在的字段: ['username', 'password', 'mobile']  # 对于模型中不存在的字段, 要自定义创建
    
    # 需要序列化的字段: ['id', 'username', 'mobile']  # 发送给前端的数据, 根据前端需求返回
    # 需要反序列化的字段: ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)
    
    class Meta:
        model = User  # 从User模型中映射序列化器字段
        # fields = '__all__'  # 指定要映射的字段
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token']
        extra_kwargs = {  # 修改字段选项
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义校检出错后信息提示
                    'min_length': '仅允许5-20字符的用户名',
                    'max_length': '仅允许5-20字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
        
    # 传入什么就返回什么
    def validate_mobile(self, value):
        """单独校检手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误')
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
        
        if not real_sms_code or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')
        
        return attrs
    
    def create(self, validated_data):
        # ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
        # 把不需要存储的 password2, sms_code, allow 从字段中移出
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        
        # 先取出password
        password = validated_data.pop('password')
        # 创建用户模型, 给模型中的 username和mobile 赋值
        user = User(**validated_data)
        user.set_password(password)  # 把密码加密再赋值给user的password属性
        user.save()  # 存储到数据库

        # 生成记录登录状态的token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        
        user.token = token
        return user  # 返回给 instance
    

class UserDetailSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')
        

class EmailSerializer(serializers.ModelSerializer):
    """更新邮箱序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True  # 该字段必须传入参数
            }
        }
    
    def update(self, instance, validated_data):
        """重写此方法不是为了修而是借此时机 发送激活邮箱 """
        instance.email = validated_data.get('email')
        instance.save()
        # 将来再次 填写发送邮箱功能
        # 使用异步任务实现邮件验证链接
        verify_url = instance.generate_email_verify_url()
        send_verify_email.delay(instance.email, verify_url)
        return instance
    

class AddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    # 序列化的字段: ['id', 'receiver', 'title', 'place', 'mobile', 'tel', 'email',
    # 'province', 'city', 'district', 'province_id', 'city_id', 'district_id']
    # read_only: 只能用于序列化
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    # required: 该字段在反序列化时必须输入
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    
    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')
    
    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号错误')
        return value

    def create(self, validate_data):
        """新增收货地址"""
        # 给谁新增, 怎么新增
        user = self.context['request'].user  # 获取用户模型对象
        validate_data['user'] = user  # 将用户模型保存到validate_data字典中
        return Address.objects.create(**validate_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    class Meta:
        model = Address
        fields = ('title',)
