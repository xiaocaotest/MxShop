import random

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin

from MxShop.settings import APIKEY
from users.models import VerifyCode
from users.serializers import SmsSerializer, UserSerializer, UserDetailSerializer
from utils.yunpian import YunPian

User = get_user_model()


class CustomBackend(ModelBackend):
    """自定义用户验证"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 使得用户名和手机号都能登录
            user = User.objects.get(
                Q(username=username) | Q(mobile=username)
            )
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """手机验证码"""
    serializer_class = SmsSerializer

    def generate_code(self):
        """生成四位数字的验证码"""
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(random.choice(seeds))

        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        """
        创建验证码
        发送验证码
        发送成功将验证码、手机号存储到模型中
        """
        serializer = self.get_serializer(data=request.data)
        # 验证合法
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)
        # 生成验证码
        code = self.generate_code()

        # 发送短信验证码
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        # 这段不需要添加（临时添加的）
        # code_record = VerifyCode(code=code, mobile=mobile)
        # code_record.save()

        # 短信验证码发送失败
        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 发送成功，保存到数据库中
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


class UserCreateViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    """
    创建用户、注册用户、修改用户信息、获取用户详情
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_permissions(self):
        """
        设置动态权限：用户注册时没有权限限制，获取用户详情必须登录才可以
        :return:
        """
        if self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action == "create":
            return []

        return []

    def get_serializer_class(self):
        """
        动态选择使用哪个序列化方式
        UserSerializer：用于用户注册，UserDetailSerializer：用于返回用户详情
        :return:
        """
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserSerializer
        return UserDetailSerializer

    def get_object(self):
        """
        获取登录用户
        用于返回用户对象，判断当前是哪个用户，配合 UserDetailSerializer 获取用户详情
        :return:
        """
        return self.request.user  # 即当前登录用户

