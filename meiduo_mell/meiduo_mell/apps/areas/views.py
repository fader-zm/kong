from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from .serializers import AreaListSerializer, AreaSerializer


# class AreaListView(APIView):
#     """查询所有省数据"""
#
#     def get(self, request):
#         # 1. 获取指定的查询集
#         queryset = Area.objects.filter(parent=None)
#         # 2. 创建序列化器进行序列化
#         serializer = AreaListSerializer(queryset, many=True)
#         # 3. 响应
#         return Response(serializer.data)
#
#
# class AreaView(APIView):
#     """查询市, 区"""
#     def get(self, request, pk):
#         # 1. 根据pk查询出指定的省或市
#         try:
#             area = Area.objects.get(id=pk)
#         except Area.DoesNotExist:
#             return Response({'massage': '无效的pk'}, status=status.HTTP_400_BAD_REQUEST)
#         # 2. 创建序列化器进行序列化
#         serializer = AreaSerializer(area)
#         # 3. 响应
#         return Response(serializer.data)
    

# class AreaListView(ListAPIView):
#     """省 列表视图"""
#     # 指定查询集
#     queryset = Area.objects.filter(parent=None)
#     # 指定序列化器
#     serializer_class = AreaListSerializer
#
#
# class AreaView(RetrieveAPIView):
#     """市, 区 详情视图"""
#     # 指定查询模型对象 因为要进行关联序列化,
#     queryset = Area.objects.all()
#     # 指定序列化器
#     serializer_class = AreaSerializer


class AreaViewSet(ReadOnlyModelViewSet):
    """使用视图集 查所有(省)和查单一(市, 县(区))"""

    # 重写 get_queryset() 方法, 指定查询集
    def get_queryset(self):
        if self.action == 'list':
            queryset = Area.objects.filter(parent=None)
        else:
            queryset = Area.objects.all()
        return queryset
    
    # 重写 get_serializer() 方法, 指定序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaListSerializer
        else:
            return AreaSerializer
            
    























