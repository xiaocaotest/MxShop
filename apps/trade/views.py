from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from trade.models import ShoppingCart, OrderGoods, OrderInfo
from trade.seriliazers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from utils.permissions import IsOwnerOrReadOnly


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能：
    list：获取购物车详情
    create：加入购物车
    delete：删除购物车记录
    """
    serializer_class = ShopCartSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    # 商品 ID，用于购物车更新（update() 商品数量）
    lookup_field = "goods_id"

    def get_queryset(self):
        """获取当前用户购物车列表"""
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """动态选择 serializer"""
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer


class OrderViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin):
    """
    订单相关
    list：获取个人订单
    create：创建订单
    delete：删除订单
    """
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        # 订单详情
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializer

    def perform_create(self, serializer):
        """
        提交订单之前步骤
            1、将购物车中商品保存到 OrderGoods
            2、清空购物车
        :param serializer:
        :return:
        """
        order = serializer.save()
        # 获取购物车中所有商品
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop.goods
            order_goods.goods_num = shop.nums
            order_goods.order = order
            order_goods.save()

            # 清空购物车
            shop.delete()

        return order

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

