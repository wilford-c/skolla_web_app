from django.contrib import admin

from .models import Assessment, Classroom, Grade, Subject


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'homeroom_teacher')
	search_fields = ('code', 'name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'classroom', 'teacher', 'weekly_sessions')
	search_fields = ('code', 'name')
	list_filter = ('classroom',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'subject', 'assessment_type', 'max_score', 'weight', 'date')
	search_fields = ('name', 'subject__name')
	list_filter = ('subject', 'assessment_type', 'date')
	date_hierarchy = 'date'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
	list_display = ('student', 'assessment', 'score', 'percentage', 'letter_grade', 'entered_at')
	search_fields = ('student__full_name', 'assessment__name')
	list_filter = ('assessment__subject', 'assessment__assessment_type', 'entered_at')
	readonly_fields = ('percentage', 'letter_grade', 'entered_at', 'updated_at')
	date_hierarchy = 'entered_at'
