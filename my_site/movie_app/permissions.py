from rest_framework.permissions import BasePermission


class CheckUserMovie(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.status == 'pro':
            return True
        elif request.user.status == 'simple' and obj.status_movie == 'simple':
            return True
        return False


class CheckUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.status == 'pro'
