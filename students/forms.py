from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from academics.models import Classroom

from .models import Student


User = get_user_model()


class StudentForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    guardian_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label='Select linked guardian (optional)',
        help_text='Link an existing guardian account for portal access.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['guardian_user'].queryset = (
            User.objects.filter(role=User.Role.GUARDIAN)
            .order_by('first_name', 'last_name')
        )
        self.fields['current_classroom'].queryset = Classroom.objects.order_by('code')

    class Meta:
        model = Student
        fields = [
            'admission_number',
            'first_name',
            'last_name',
            'date_of_birth',
            'current_classroom',
            'guardian_name',
            'guardian_user',
            'contact_email',
            'contact_phone',
            'status',
        ]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with student data. Required columns: admission_number, first_name, last_name, date_of_birth, guardian_name',
        widget=forms.FileInput(attrs={'accept': '.csv'}),
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if not csv_file:
            raise forms.ValidationError('No file was uploaded.')
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        # Check file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must not exceed 5MB.')
        
        return csv_file


class StudentTransferForm(forms.Form):
    new_classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        label='New classroom',
    )
    effective_date = forms.DateField(
        label='Effective date',
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    note = forms.CharField(
        label='Transfer note',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional transfer note'}),
    )

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        classrooms = Classroom.objects.order_by('code')
        if student and student.current_classroom_id:
            classrooms = classrooms.exclude(pk=student.current_classroom_id)
        self.fields['new_classroom'].queryset = classrooms

    def clean_new_classroom(self):
        classroom = self.cleaned_data['new_classroom']
        if self.student and classroom.pk == self.student.current_classroom_id:
            raise forms.ValidationError('Select a different classroom to transfer the student.')
        return classroom
