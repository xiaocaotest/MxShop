import re
from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import VerifyCode, UserProfile
from MxShop.settings import REGEX_MOBILE


class SmsSerializer(serializers.Serializer):
    """短信验证"""
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        手机号码验证：函数名必须为 validate_验证字段名
        :param mobile:
        :return:
        """
        # 手机号是否已注册
        if UserProfile.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已存在")

        # 手机号格式是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号格式非法")

        # 验证码频率，1min 只能发一次
        one_min_time = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)

        # 从数据库中取出验证码，view 中生成验证码并发送成功后，会将验证码存储到 VerifyCode 模型中，这里只需取出验证时间即可
        if VerifyCode.objects.filter(add_time__gt=one_min_time, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return mobile


class UserSerializer(serializers.ModelSerializer):
    """用户注册"""
    # UserProfile 中没有 Code 字段，自定义一个
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, error_messages={
        "blank": "请输入验证码",
        "required": "请输入验证码",
        "max_length": "验证码格式错误",
        "min_length": "验证码格式错误"
    }, help_text="验证码")

    # 验证用户名
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="用户名已存在")])

    # 添加 password 字段
    password = serializers.CharField(style={'input_type': 'password'}, label="密码", write_only=True)

    def create(self, validated_data):
        """密码加密保存"""
        user = super(UserSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_code(self, code):
        """
        验证验证码
        post 数据都保存在 initial_data 里，username 为用户注册的手机号，验证码
        按添加时间倒序排序，为了后面验证过期，错误等
        :param code:
        :return:
        self.initial_data：{'password': 'abcd110139', 'username': '18674447633', 'code': '6188'}
        """
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data['mobile']).order_by('-add_time')

        if verify_records:
            # 最近的一个验证码
            last_record = verify_records[0]
            # 有效期为 5 min
            five_mintues_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintues_ago > last_record.add_time.replace(tzinfo=None):
                raise serializers.ValidationError('验证码过期！')

            if last_record.code != code:
                raise serializers.ValidationError(f'验证码错误！')
        else:
            raise serializers.ValidationError('验证码错误！')

    def validate(self, attrs):
        """
        验证所有字段，attr 为验证合法后返回的 dict
        :param self:
        :param attrs:
        :return:
        """
        # 前端没有传 mobile 值到后端，添加进来
        attrs['mobile'] = attrs['username']

        # 模型中没有 code 字段，验证完之后，删除
        del attrs['code']
        return attrs

    class Meta:
        model = UserProfile
        # 前端显示的字段
        fields = ('username', 'code', 'mobile', 'password')


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情：用于用户个人中心"""
    class Meta:
        model = UserProfile
        fields = ("name", "birthday", "gender", "email", "mobile")
