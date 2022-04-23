from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer

from goods.models import Goods, GoodsCategory, GoodsImage


class CategorySerializer(serializers.ModelSerializer):
    """
    分类
    """

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsImageSerializer(serializers.ModelSerializer):
    """商品详情中的轮播图"""

    class Meta:
        model = GoodsImage
        fields = ('image',)


class GoodsSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    """
    商品列表页
    """
    # 覆盖外键字段
    category = CategorySerializer()

    # 商品轮播图，覆盖外键字段，这里使用的 related_name='images'
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        fields = '__all__'
