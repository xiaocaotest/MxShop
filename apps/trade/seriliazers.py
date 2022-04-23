from rest_framework import serializers

from goods.models import Goods
from goods.serializers import GoodsSerializer
from trade.models import ShoppingCart, OrderGoods, OrderInfo


class ShopCartSerializer(serializers.Serializer):
    """购物车"""
    # 获取当前登录用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        'min_value': '商品数量不能小于一',
                                        'required': '请选择购买数量'
                                    })
    # 外键，获取 goods 中所有值，必须指定 queryset，继承 ModelSerializer 无需指定
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def create(self, validated_data):
        """
        serializers.Serializer 没有 save() 需要重写 create
        :param validated_data:已处理过的数据（前端提交的数据）
        :return:
        """
        # 获取当前用户
        user = self.context['request'].user
        nums = validated_data['nums']
        goods = validated_data['goods']

        # 查询数据库，若有记录（表示添加到购物车，该商品），数量 + nums，否则就添加到购物车
        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        # 数量增加
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            # 添加到购物车
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        """更新购物车，修改数量"""
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class ShopCartDetailSerializer(serializers.ModelSerializer):
    """购物车中商品详情"""
    # 一个购物车对应一个商品.
    goods = GoodsSerializer(many=False, required=True)

    class Meta:
        model = ShoppingCart
        fields = ('goods', 'nums')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单中的商品"""
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    订单中商品详细信息
    """
    # goods字段需要嵌套一个OrderGoodsSerializer
    goods = OrderGoodsSerializer(many=True)
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """订单"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 生成订单时，不需 post以下数据
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    nonce_str = serializers.CharField(read_only=True)
    pay_type = serializers.CharField(read_only=True)

    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def generate_order_sn(self):
        """
        生成订单号：当前时间+userid+随机数
        :return:
        """
        import time
        from random import Random
        random_str = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context['request'].user.id,
                                                       ranstr=random_str.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        """validate 中添加 order_sn，然后再 view 中就可以 save"""
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'

