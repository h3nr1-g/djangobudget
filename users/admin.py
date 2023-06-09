from django.contrib import admin

# Register your models here.
from users.models import Role, UserRole


class UserRoleEntryAdmin(admin.ModelAdmin):
    list_display = ('budget', 'user', 'role')


admin.site.register(Role)
admin.site.register(UserRole, UserRoleEntryAdmin)