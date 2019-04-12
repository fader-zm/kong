from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    """
    自定义用户模型类
    """
    # unique: 数据必须唯一  verbose_name: admin站点显示的别名
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')  # 用于标识该用户邮箱是否通过验证
    
    class Meta:  # 配置数据库表名及设置模型在admin站点显示的中文名
        db_table = 'tb_users'  # 数据库表名
        verbose_name = '用户'  # 模型admin站点显示的中文名
        verbose_name_plural = verbose_name  # 模型名称的复数形式, 如果不指定Django会自动在模型名称后加一个's'
    
    def generate_email_verify_url(self):
        """用户邮箱验证 url 生成"""
        # 1. 创建加密的序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600*24)
        # 2. 调用dumps方法进行加密 bytes
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        # 3. 拼接url 返回
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
    
    @staticmethod
    def check_verify_email_token(token):
        """解密token, 并返回user"""
        # 1. 创建解密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600*24)
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
