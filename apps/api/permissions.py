import logging

from rest_framework.permissions import BasePermission, IsAuthenticated

logger = logging.getLogger('api.permissions')


class OnlyOwnerCanRead(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        assert getattr(view, 'owner_field', None) is not None, \
            f"Define 'owner_field' view attribute to use {self.__class__.__name__} permission"

        try:
            user = getattr(obj, f'{view.owner_field}_id)')
        except AttributeError:
            try:
                user = getattr(obj, f'{view.owner_field}')
            except AttributeError:
                logging.getLogger(f"Object returned by view {view.__class__.__name__} has't got field owner field"
                                  f"'{view.owner_field}', denying access")
                return False

        # If no relation, deny
        if user is None:
            return False

        return request.user.pk == user or request.user == user


class OnlyOwnerCanChange(OnlyOwnerCanRead):
    safe_actions = ('detail', 'retrieve', 'head', 'options')

    def has_object_permission(self, request, view, obj):
        assert getattr(view, 'action', None) is not None,\
            f"{self.__class__.__name__} permission is compatible only with ViewSets (or other Views defining action"
        if view.action in self.safe_actions:
            return True
        return super().has_object_permission(request, view, obj)
