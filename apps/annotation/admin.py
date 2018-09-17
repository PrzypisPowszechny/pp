from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

from apps.annotation.models import Annotation
from apps.annotation.models import AnnotationRequest

admin.site.register(get_user_model(), UserAdmin)


class AnnotationAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Annotation, AnnotationAdmin)


class AnnotationRequestAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(AnnotationRequest, AnnotationRequestAdmin)
