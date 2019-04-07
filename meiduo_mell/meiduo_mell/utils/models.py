from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""
    # DateTimeField: 日期时间
    # auto_now_add: 表示当对象第一次被创建时自动设置当前时间，用于创建的时间戳，它总是使用当前日期，默认为False
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # auto_now: 表示每次保存对象时，自动设置该字段为当前时间，用于"最后一次修改"的时间戳，它总是使用当前日期，默认为False
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        abstract = True  # 说明此类是抽象模型类, 用于继承使用, 数据库迁移时不会创建BaseModel的表
