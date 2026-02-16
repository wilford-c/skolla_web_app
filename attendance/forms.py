from django import forms

from .models import AttendanceRecord


class AttendanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = AttendanceRecord
        fields = ['student', 'classroom', 'subject', 'date', 'status', 'notes']
