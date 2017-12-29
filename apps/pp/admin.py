from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from apps.pp.models import Reference
from apps.pp.models import ReferenceRequest
from apps.pp.models import UserReferenceFeedback

admin.site.register(get_user_model(), UserAdmin)


class ReferenceAdmin(SimpleHistoryAdmin):
    def useful(self, inst):
        return UserReferenceFeedback.objects.filter(reference=inst).filter(useful=True).count()

    def objection(self, inst):
        return UserReferenceFeedback.objects.filter(reference=inst).filter(objection=True).count()

    list_display = ('comment', 'create_date', 'user', 'useful', 'objection', 'priority', 'active')
    list_editable = ('active',)
    search_fields = ('comment', 'quote', 'reference_link',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username[0].upper() != 'J':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Reference, ReferenceAdmin)


class ReferenceRequestAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'url', 'active')
    list_editable = ('active',)
    search_fields = ('user', 'url')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username[0].upper() != 'J':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ReferenceRequest, ReferenceRequestAdmin)
admin.site.site_header = 'Przypis Powszechny Administrator'
