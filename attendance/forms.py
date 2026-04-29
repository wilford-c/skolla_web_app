from django import forms

from academics.models import Classroom, Subject
from students.models import Student

from .models import AttendanceRecord, NotificationPreference, ReportTemplate


class AttendanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = AttendanceRecord
        fields = ['student', 'classroom', 'subject', 'date', 'status', 'notes']


class ReportBuilderForm(forms.Form):
	"""Form for building custom attendance reports."""
	
	# Available fields that can be included in the report
	FIELD_CHOICES = [
		('date', 'Date'),
		('student_admission_number', 'Admission Number'),
		('student_name', 'Student Name'),
		('classroom', 'Classroom'),
		('subject', 'Subject'),
		('status', 'Attendance Status'),
		('notes', 'Notes'),
		('recorded_by', 'Recorded By'),
		('recorded_at', 'Recorded At'),
	]
	
	EXPORT_FORMATS = [
		('csv', 'CSV'),
		('xlsx', 'Excel (XLSX)'),
		('pdf', 'PDF'),
	]
	
	# Report name (for saving as template)
	report_name = forms.CharField(
		max_length=120,
		required=False,
		help_text='Optional: Save this report configuration as a template'
	)
	
	# Field selection
	fields = forms.MultipleChoiceField(
		choices=FIELD_CHOICES,
		widget=forms.CheckboxSelectMultiple,
		initial=['date', 'student_name', 'classroom', 'subject', 'status'],
		help_text='Select fields to include in the report'
	)
	
	# Filters
	date_from = forms.DateField(
		required=False,
		widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		help_text='Start date for the report'
	)
	date_to = forms.DateField(
		required=False,
		widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		help_text='End date for the report'
	)
	classroom = forms.ModelChoiceField(
		queryset=Classroom.objects.all(),
		required=False,
		empty_label='All Classrooms',
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	subject = forms.ModelChoiceField(
		queryset=Subject.objects.all(),
		required=False,
		empty_label='All Subjects',
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	student = forms.ModelChoiceField(
		queryset=Student.objects.filter(status=Student.Status.ACTIVE).order_by('admission_number'),
		required=False,
		empty_label='All Students',
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	status = forms.ChoiceField(
		choices=[('', 'All Statuses')] + list(AttendanceRecord.Status.choices),
		required=False,
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	
	# Grouping and sorting
	grouping = forms.ChoiceField(
		choices=ReportTemplate.Grouping.choices,
		required=False,
		initial=ReportTemplate.Grouping.NONE,
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	sorting = forms.ChoiceField(
		choices=ReportTemplate.Sorting.choices,
		required=False,
		initial=ReportTemplate.Sorting.DATE_DESC,
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	
	# Export options
	export_format = forms.ChoiceField(
		choices=EXPORT_FORMATS,
		initial='csv',
		widget=forms.RadioSelect,
		help_text='Select export format'
	)
	
	include_summary = forms.BooleanField(
		required=False,
		initial=True,
		help_text='Include summary statistics at the end of the report'
	)
	
	save_as_template = forms.BooleanField(
		required=False,
		initial=False,
		help_text='Save this configuration as a reusable template'
	)


class ReportTemplateForm(forms.ModelForm):
	"""Form for creating/editing report templates."""
	
	class Meta:
		model = ReportTemplate
		fields = ['name', 'description', 'fields', 'filters', 'grouping', 'sorting', 'is_shared']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
			'fields': forms.HiddenInput(),
			'filters': forms.HiddenInput(),
			'grouping': forms.Select(attrs={'class': 'form-control'}),
			'sorting': forms.Select(attrs={'class': 'form-control'}),
			'is_shared': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
		}


class NotificationPreferenceForm(forms.ModelForm):
	"""Form for guardians to manage their notification preferences."""
	
	class Meta:
		model = NotificationPreference
		fields = ['mode', 'notify_absent', 'notify_late', 'notify_excused', 'email', 'is_enabled']
		widgets = {
			'mode': forms.RadioSelect(),
		}
		help_texts = {
			'email': 'Leave blank to use your account email address',
		}
