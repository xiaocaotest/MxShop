from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from goods.serializers import GoodsSerializer
from user_operation.models import UserFav, UserLeavingMessage, UserAddress


class UserFavSerializer(serializers.ModelSerializer):
    """用户收藏商品"""
    # 获取当前登录用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        # validate 实现唯一联合，一个商品只能收藏一次
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"  # 自定义提示信息
            )
        ]
        model = UserFav
        # 返回商品 ID，用于取消收藏
        fields = ('user', 'goods', 'id')


class UserFavDetailSerializer(serializers.ModelSerializer):
    """
    收藏详情
    """
    # 通过商品 id 获取收藏的商品，需要嵌套商品的序列化
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ('goods', 'id')


class UserLeavingMessageSerializer(serializers.ModelSerializer):
    """用户留言"""
    # 获取当前登录用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # read_only:只返回，post时候可以不用提交，format：格式化输出
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserLeavingMessage
        fields = ('user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time')


class UserAddressSerializer(serializers.ModelSerializer):
    """用户地址"""
    # 获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserAddress
        fields = ('user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'add_time', 'id')

