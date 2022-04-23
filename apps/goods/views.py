from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from goods.serializers import GoodsSerializer
from .models import Goods
from .filters import GoodsFilter


# class GoodsPagination(PageNumberPagination):
#     """
#     自定义商品列表分页
#     """
#     page_size = 10  # 每页显示个数
#     page_size_query_param = 'page_size'  # 可以动态改变每页显示的个数
#     page_query_param = 'page'  # 页码参数
#     max_page_size = 100  # 最多能显示多少页


class GoodsListViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    """
    商品列表
    """
    # 分页
    # pagination_class = GoodsPagination
    # # 这里必须要定义一个默认的排序,否则会报错
    # queryset = Goods.objects.all().order_by('id')
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # 过滤
    filter_backends = (DjangoFilterBackend, SearchFilter,)

    # 设置 filter 的类为自定义的类
    filter_class = GoodsFilter

    # 搜索，=name 为精确搜索，也可以使用正则
    search_fields = ('=name', 'goods_brief')

    # 排序
    ordering_fields = ('sold_num', 'add_time')

