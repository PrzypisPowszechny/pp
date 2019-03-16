import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger('api.permissions')


class IsUserOwner(BasePermission):

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
