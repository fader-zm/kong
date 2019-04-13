from rest_framework import serializers
from .models import Area


class AreaListSerializer(serializers.ModelSerializer):
    """省序列化器"""
    """列表视图序列化器"""
    class Meta:
        model = Area
        fields = ('id', 'name')


class AreaSerializer(serializers.ModelSerializer):
    """市, 区 序列化器"""
    """详情视图序列化器"""
    # 关联序列化: 从一里面拿多 subs是多的一放
    # subs = serializers.PrimaryKeyRelatedField()  # 只会序列化出 id
    # subs = serializers.StringRelatedField()  # 序列化的时模型中str方法返回值
    subs = AreaListSerializer(many=True)
    
    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')
