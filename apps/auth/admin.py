from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class UserChangeForm(auth_admin.UserChangeForm):
    class Meta(auth_admin.UserChangeForm.Meta):
        model = get_user_model()


@admin.register(get_user_model())
class UserAdmin(auth_admin.UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    form = UserChangeForm
