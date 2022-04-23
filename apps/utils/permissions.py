from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # 允许任何请求读取权限
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj 相当于 model，将 owner 改为 user
        return obj.user == request.user
