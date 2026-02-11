from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobRole, RoleAssignment, DiagnosticSubmission, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(JobRole)
admin.site.register(RoleAssignment)
admin.site.register(DiagnosticSubmission)
admin.site.register(Notification)