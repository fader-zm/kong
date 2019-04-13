from django.db import models


# Create your models here.
class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20, verbose_name='名称')
    # blank: 如果为True，则该字段允许为空白，默认值是False admin站点运营时可以为空白, 写入数据的是一个空的字符串
    # on_delete: 在设置外键时，需要通过on_delete选项指明主表删除数据时，对于外键引用表数据如何处理
    # SET_NULL 在父表上update/delete记录时，将子表上匹配记录的列设为null
    # related_name: 该外键定义好名称, 方便主表调用
    # null: 允许字段为空
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')
    
    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name
