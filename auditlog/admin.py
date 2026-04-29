from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "action",
        "entity_type",
        "entity_id",
        "severity",
        "ip_address",
    )
    list_filter = ("severity", "action", "entity_type", "created_at")
    search_fields = ("action", "entity_type", "entity_id", "description", "user__username")
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "user",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "metadata",
        "severity",
        "ip_address",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
