from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('admission_number', 'full_name', 'status', 'guardian_name', 'contact_phone')
	list_filter = ('status',)
	search_fields = ('admission_number', 'first_name', 'last_name', 'guardian_name')
