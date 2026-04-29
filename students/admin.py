from django.contrib import admin

from .models import Enrollment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('admission_number', 'full_name', 'status', 'guardian_name', 'contact_phone')
	list_filter = ('status',)
	search_fields = ('admission_number', 'first_name', 'last_name', 'guardian_name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = (
		'student',
		'classroom',
		'status',
		'start_date',
		'end_date',
		'onboarded_by',
	)
	list_filter = ('status', 'classroom')
	search_fields = (
		'student__admission_number',
		'student__first_name',
		'student__last_name',
		'classroom__code',
		'classroom__name',
	)
