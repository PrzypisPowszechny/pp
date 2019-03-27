import logging

from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger('api.permissions')

# Action equivalent of GET (single and multiple objects), HEAD (same as get) and OPTIONS
read_actions = ('list', 'retrieve', 'metadata')


class ViewSetRequiredMixin:
    def assert_viewset(self, view):
        assert getattr(view, 'action', None) is not None, \
            f"{self.__class__.__name__} permission is compatible only with ViewSets (or other Views defining action"


class OnlyOwnerCanRead(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        assert getattr(view, 'owner_field', None) is not None, \
            f"Define 'owner_field' view attribute to use {self.__class__.__name__} permission"

        try:
            user = getattr(obj, f'{view.owner_field}_id')
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


class OnlyOwnerCanWrite(ViewSetRequiredMixin, OnlyOwnerCanRead):

    def has_object_permission(self, request, view, obj):
        self.assert_viewset(view)
        if view.action in read_actions:
            return True

        return super().has_object_permission(request, view, obj)


class OnlyEditorCanWrite(ViewSetRequiredMixin, IsAuthenticated):
    def has_permission(self, request, view):
        self.assert_viewset(view)
        if view.action in read_actions:
            return True
        return request.user.role == request.user.ROLE_EDITOR
