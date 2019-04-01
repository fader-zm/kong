from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """
    自定义用户模型类
    """
    # unique: 数据必须唯一  verbose_name: admin站点显示的别名
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    
    class Meta:  # 配置数据库表名及设置模型在admin站点显示的中文名
        db_table = 'tb_users'  # 数据库表名
        verbose_name = '用户'  # 模型admin站点显示的中文名
        verbose_name_plural = verbose_name  # 模型名称的复数形式, 如果不指定Django会自动在模型名称后加一个's'
