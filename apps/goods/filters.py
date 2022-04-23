import django_filters

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品过滤
    """
    # field_name 为要过滤的字段，lte 为执行的行为，这里为小于等于本店价格
    price_min = django_filters.NumberFilter(field_name='shop_price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='shop_price', lookup_expr='lte')

    class Meta:
        model = Goods
        fields = ['price_min', 'price_max', 'is_hot']
