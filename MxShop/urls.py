"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from MxShop.settings import MEDIA_ROOT
from goods.views import GoodsListViewSet
from trade.views import ShoppingCartViewSet, OrderViewSet
from user_operation.views import UserFavViewSet, UserLeavingMessageViewSet, UserAddressViewSet
from users.views import SmsCodeViewSet, UserCreateViewSet

router = DefaultRouter()

router.register(r'goods', GoodsListViewSet, basename='goods')
router.register(r'code', SmsCodeViewSet, basename="code")   # 短信验证码
router.register(r'users', UserCreateViewSet, basename='users')   # 注册
router.register(r'userfavs', UserFavViewSet, basename='userfavs')   # 用户商品收藏
router.register(r'messages', UserLeavingMessageViewSet, basename='message')  # 用户留言
router.register(r'address', UserAddressViewSet, basename='address')  # 收藏地址
router.register(r'shopcarts', ShoppingCartViewSet, basename='shopcarts')  # 购物车
router.register(r'orders', OrderViewSet, basename='orders')  # 订单


urlpatterns = [
    path('admin/', admin.site.urls),
    path('media/<path:path>', serve, {'document_root': MEDIA_ROOT}),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # drf 文档
    path('docs', include_docs_urls(title='hubery')),
    path('api-auth/', include('rest_framework.urls')),

    re_path('^', include(router.urls)),
]
