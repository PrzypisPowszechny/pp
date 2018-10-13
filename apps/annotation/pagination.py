from rest_framework.pagination import BasePagination


class ConstantLimitPagination(BasePagination):
    """
    A limit/offset based style. For example:

    """
    constant_limit = 100

    def paginate_queryset(self, queryset, request, view=None):
        return queryset[:self.constant_limit]
