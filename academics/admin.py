from django.contrib import admin

from .models import Classroom, Subject


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'homeroom_teacher')
	search_fields = ('code', 'name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'classroom', 'teacher', 'weekly_sessions')
	search_fields = ('code', 'name')
	list_filter = ('classroom',)
