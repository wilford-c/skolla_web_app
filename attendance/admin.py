from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ('student', 'classroom', 'subject', 'date', 'status', 'recorded_by')
	list_filter = ('status', 'date', 'classroom')
	search_fields = ('student__first_name', 'student__last_name', 'subject__name')
