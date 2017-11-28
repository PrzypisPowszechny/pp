from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

from apps.pp.models import Reference
from apps.pp.models import ReferenceRequest

admin.site.register(get_user_model(), UserAdmin)


class ReferenceAdmin(SimpleHistoryAdmin):
    pass

admin.site.register(Reference, ReferenceAdmin)


class ReferenceRequestAdmin(SimpleHistoryAdmin):
    pass

admin.site.register(ReferenceRequest, ReferenceRequestAdmin)