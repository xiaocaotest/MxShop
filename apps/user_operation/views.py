from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from user_operation.models import UserFav, UserLeavingMessage, UserAddress
from user_operation.serializers import UserFavSerializer, UserFavDetailSerializer, UserLeavingMessageSerializer, \
    UserAddressSerializer
from utils.permissions import IsOwnerOrReadOnly


class UserFavViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """
    用户商品收藏
    ListModelMixin：收藏列表
    CreateModelMixin：收藏
    DestroyModelMixin：取消（删除）收藏，相应地要删除数据库中数据
    """
    serializer_class = UserFavSerializer
    queryset = UserFav.objects.all()

    # IsAuthenticated：必须登录用户；IsOwnerOrReadOnly：必须是当前登录的用户
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 用户认证
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    # 搜索的字段
    lookup_field = 'goods_id'

    def get_serializer_class(self):
        """
        动态设置 serializer，get 时获取用户收藏详情
        :return:
        """
        if self.action == 'list':
            # 收藏列表
            return UserFavDetailSerializer
        elif self.action == 'create':
            return UserFavSerializer

        return UserFavSerializer

    def get_queryset(self):
        # 只能查看当前登录用户的收藏，禁止获取其他用户的收藏
        return UserFav.objects.filter(user=self.request.user)


class UserLeavingMessageViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                                mixins.DestroyModelMixin):
    """
    用户留言：添加留言、删除留言、留言列表
    """
    serializer_class = UserLeavingMessageSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_queryset(self):
        """用户只能看自己的留言"""
        return UserLeavingMessage.objects.filter(user=self.request.user)


class UserAddressViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    用户收件地址：新增地址（CreateModelMixin）、删除地址（DestroyModelMixin）
    、所有地址（ListModelMixin）、更新地址（UpdateModelMixin）
    """
    serializer_class = UserAddressSerializer
    authentication_classes = (JWTAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        """用户只能查看自己的收藏地址"""
        return UserAddress.objects.filter(user=self.request.user)
