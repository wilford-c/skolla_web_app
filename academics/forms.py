from django import forms

from .models import Classroom, Subject


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'code', 'homeroom_teacher', 'description']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'classroom', 'teacher', 'weekly_sessions']
