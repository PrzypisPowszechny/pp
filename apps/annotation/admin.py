from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

from apps.annotation.models import Annotation
from apps.annotation.models import AnnotationRequest
from urllib.parse import urlparse
admin.site.register(get_user_model(), UserAdmin)


def truncate(string, allowed_max=20):
    if len(string) > allowed_max:
        return string[:allowed_max] + '...'
    else:
        return string


def truncate_url(string, allowed_max):
    try:
        p = urlparse(string)
    except:
        return 'Incorrect URL, error parsing'
    domain = p.netloc[4:] if p.netloc.startswith('www.') else p.netloc
    return domain + truncate(p.path, allowed_max)


class AnnotationAdmin(SimpleHistoryAdmin):
    date_hierarchy = 'create_date'
    list_display = ('short_url', 'publisher', 'short_quote', 'active', 'annotation_link_title', 'create_date', 'short_annotation_link', 'short_comment', 'count_upvote')
    list_filter = ('active',)
    fields = ('user', 'url', 'publisher', 'quote', 'active', 'annotation_link_title', 'create_date', 'annotation_link', 'comment', 'count_upvote')
    readonly_fields = ('user', 'create_date', 'count_upvote')

    url_path_max_chars = 20
    def short_url(self, obj):
        return truncate_url(obj.url, self.url_path_max_chars)

    quote_max_chars = 40
    def short_quote(self, obj):
        return truncate(obj.quote, self.quote_max_chars)

    annotation_link_path_max_chars = 10
    def short_annotation_link(self, obj):
        return truncate_url(obj.annotation_link, self.annotation_link_path_max_chars)

    comment_max_chars = 15
    def short_comment(self, obj):
        return truncate(obj.quote, self.comment_max_chars)


admin.site.register(Annotation, AnnotationAdmin)


class AnnotationRequestAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(AnnotationRequest, AnnotationRequestAdmin)
