from django.db import models
from meiduo_mell.utils.models import BaseModel

from users.models import User

# Create your models here.


class OauthQQUser(BaseModel):
    """
    QQ登录用户数据
    """
    # ForeignKey: 设置外键
    # on_delete: 指明主表删除数据时，对于外键引用表数据如何处理
    # CASCADE 级联，删除主表数据时连通一起删除外键表中数据
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    # db_index: 若值为True, 则在表中会为此字段创建索引，默认值是False
    # 对于频繁查询的字段, 创建索引能够提升查询效率
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    
    class Meta:
        db_table = 'tb_oauth_qq'  # 指明数据库表名
        verbose_name = '用户登录数据'  # 显示admin站点中的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

