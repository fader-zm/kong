from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from meiduo_mell.utils.models import BaseModel

# Create your models here.


class User(AbstractUser):
    """
    自定义用户模型类
    """
    # unique: 数据必须唯一  verbose_name: admin站点显示的别名
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')  # 用于标识该用户邮箱是否通过验证
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:  # 配置数据库表名及设置模型在admin站点显示的中文名
        db_table = 'tb_users'  # 数据库表名
        verbose_name = '用户'  # 模型admin站点显示的中文名
        verbose_name_plural = verbose_name  # 模型名称的复数形式, 如果不指定Django会自动在模型名称后加一个's'
    
    def generate_email_verify_url(self):
        """用户邮箱验证 url 生成"""
        # 1. 创建加密的序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)
        # 2. 调用dumps方法进行加密 bytes
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        # 3. 拼接url 返回
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
    
    @staticmethod
    def check_verify_email_token(token):
        """解密token, 并返回user"""
        # 1. 创建解密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)
        # 2. 调用loads解密
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        user_id = data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        else:
            return user


class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

