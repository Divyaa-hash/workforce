from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobRole, RoleAssignment, DiagnosticSubmission, Notification, AuditLog

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


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'event_type', 'user', 'entity_type', 'entity_id')
    list_filter = ('event_type', 'entity_type', 'created_at')
    search_fields = ('event_type', 'user__username', 'entity_type')
    readonly_fields = ('created_at',)