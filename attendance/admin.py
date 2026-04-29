from django.contrib import admin

from .models import AttendanceRecord, EmailLog, NotificationPreference, ReportTemplate


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ('student', 'classroom', 'subject', 'date', 'status', 'recorded_by')
	list_filter = ('status', 'date', 'classroom')
	search_fields = ('student__first_name', 'student__last_name', 'subject__name')


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_by', 'is_shared', 'grouping', 'sorting', 'created_at')
	list_filter = ('is_shared', 'grouping', 'sorting', 'created_at')
	search_fields = ('name', 'description', 'created_by__username')
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		('Basic Information', {
			'fields': ('name', 'description', 'created_by')
		}),
		('Report Configuration', {
			'fields': ('fields', 'filters', 'grouping', 'sorting')
		}),
		('Sharing', {
			'fields': ('is_shared',)
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
	list_display = ('user', 'mode', 'is_enabled', 'notify_absent', 'notify_late', 'notify_excused', 'email')
	list_filter = ('mode', 'is_enabled', 'notify_absent', 'notify_late', 'notify_excused')
	search_fields = ('user__username', 'user__email', 'email')
	readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
	list_display = ('recipient_email', 'subject', 'status', 'sent_at')
	list_filter = ('status', 'sent_at')
	search_fields = ('recipient_email', 'subject', 'recipient__username')
	readonly_fields = ('sent_at',)
	fieldsets = (
		('Email Information', {
			'fields': ('recipient', 'recipient_email', 'subject', 'attendance_record')
		}),
		('Status', {
			'fields': ('status', 'error_message', 'sent_at')
		}),
	)
